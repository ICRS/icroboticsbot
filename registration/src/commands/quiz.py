from dataclasses import dataclass, field
from typing import List
from discord.ui import View, Select
import os


import discord
import random
import requests
from src.utils import SERVER_IP
from src.utils.induction_utils import fullInduction


DATABASE_ADAPTER_IP = os.getenv("SERVER_IP")


@dataclass
class Asset:
    media: str
    type: str
    data: str


@dataclass
class Question:
    question: str
    correct_options: List[str]
    incorrect_options: List[str]
    num_answers: int = 1
    single_choice: bool = False
    assets: List[Asset] = field(default_factory=lambda: [])


def parse_questions(questions) -> List[Question]:
    l: List[Question] = []
    for q in questions:
        l.append(Question(
            q["question"],
            q["correct_options"],
            q["incorrect_options"],
            q["num_answers"],
            q["single_choice"],
        ))

        l[-1].assets += [Asset(**c) for c in q["assets"]]

    return l


class QuizSelectList(Select):
    def __init__(
            self,
            correct_options: List[str],
            incorrect_options: List[str],
            return_callback=lambda x: None,
            single_choice: bool = False,
            **kwargs):
        super().__init__(
            min_values=1,
            max_values=1 if single_choice else len(
                incorrect_options) + len(correct_options),
            **kwargs)

        self.correct_options = correct_options
        self.incorrect_options = incorrect_options

        options = self.incorrect_options + self.correct_options
        random.shuffle(options)

        for option in options:
            self.add_option(label=option, value=option, )

        self.return_callback = return_callback

    async def callback(self, interaction):
        v = interaction.data.values().mapping
        v = v.get("values", [])

        correct = int(set(self.correct_options) == set(v))
        await interaction.response.defer()
        await self.return_callback(correct)


class QuizQuestion(View):
    def __init__(
            self,
            correct_options: List[str],
            incorrect_options: List[str],
            return_callback,
            single_choice=False,
            *, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.add_item(
            QuizSelectList(
                correct_options,
                incorrect_options,
                return_callback=return_callback,
                single_choice=single_choice))


class QuizReset(View):
    def __init__(
            self,
            return_callback,
            *, timeout: float | None = None):
        super().__init__(timeout=timeout)

        self.return_callback = return_callback

    @discord.ui.button(style=discord.ButtonStyle.red, label='Reset',)
    async def reset_quiz(self, interaction, button):
        await interaction.response.defer()
        await self.return_callback()


class Quiz:
    def __init__(
            self,
            interaction: discord.Interaction,
            shortcode: str) -> None:
        result = requests.get(SERVER_IP + "/induction/quiz")
        self.questions = parse_questions(result.json())
        self.index = 0
        self.num_questions = len(self.questions)

        self.num_correct = 0
        self.interaction = interaction
        self.user_id = str(interaction.user.id)
        self.member = interaction.user

        self.shortcode = shortcode

        self.message: discord.Message | None = None
        self.incorrect_ind: List[int] = []

    async def reset(self):
        self.index = 0
        self.num_correct = 0
        self.incorrect_ind.clear()
        await self.send_next_question()

    async def question_callback(self, correct: bool):
        self.num_correct += correct
        if not correct:
            self.incorrect_ind.append(self.index)

        if self.index >= self.num_questions:
            return await self.quiz_completed()
        else:
            await self.send_next_question()

    async def send_next_question(self):
        q = self.questions[self.index]
        question = QuizQuestion(
            q.correct_options,
            q.incorrect_options,
            return_callback=self.question_callback,
            single_choice=q.single_choice
        )
        q_embed = discord.Embed(
            title=f"Question {self.index + 1}",
            description=q.question,
            color=discord.Color.blue(),
        )
        if q.assets:
            q_embed.set_image(url=q.assets[0].data)

        if not self.index and not self.message:
            await self.interaction.response.send_message(  # noqa: E501
                embed=q_embed,
                view=question,
                ephemeral=True
            )
            self.message: discord.Message | None = await self.interaction.original_response()  # noqa: E501
        else:
            await self.message.edit(
                embed=q_embed,
                view=question,
                delete_after=None,
            )

        self.index += 1

    async def quiz_completed(self):
        if self.num_correct == self.num_questions:
            await fullInduction(self.interaction, self.shortcode, self.member)

        else:
            print(self.incorrect_ind)
            message = f"{self.num_correct}/{self.num_questions} correct. Please try again!\n\n"  # noqa: E501
            message += "You got the following incorrect:\n"
            message += "\n".join([
                "- " + self.questions[i - 1].question.strip()
                for i in self.incorrect_ind])
            q_embed = discord.Embed(
                title="Quiz not passed!",
                description=message,
                color=discord.Color.red(),
            )

            await self.message.edit(
                embed=q_embed,
                view=QuizReset(self.reset),
            )


async def launch_quiz(interaction: discord.Interaction, shortcode: str):
    quiz = Quiz(interaction=interaction, shortcode=shortcode)
    return await quiz.send_next_question()
