from dataclasses import dataclass
from typing import List
from discord.ui import View, Select

import discord
import random
import requests

from src.commands.stats import SERVER_IP

result = requests.get(SERVER_IP + "/induction/quiz")
questions = result.json()


@dataclass
class Question:
    question: str
    correct_options: List[str]
    incorrect_options: List[str]
    num_answers: int = 1
    single_choice: bool = False


questions: List[Question] = [
    Question(
        q["question"],
        q["correct_options"],
        q["incorrect_options"],
        q["num_answers"],
        q["single_choice"]
    )
    for q in questions
]


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

        correct = (set(self.correct_options) == set(v))
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
    def __init__(self, interaction: discord.Interaction) -> None:
        self.questions = questions
        self.index = 0
        self.num_questions = len(self.questions)

        self.num_correct = 0
        self.interaction = interaction
        self.user_id = str(interaction.user.id)

        self.message: discord.Message | None = None

    async def reset(self):
        self.index = 0
        self.num_correct = 0
        await self.send_next_question()

    async def question_callback(self, correct: bool):
        self.num_correct += correct
        print(self.num_correct)
        await self.send_next_question()

    async def send_next_question(self):
        if self.index >= self.num_questions:
            if self.num_correct == self.num_questions:
                response = requests.post(
                    SERVER_IP + "/induction/induct/discord-id",
                    params={"id": str(self.user_id)})

                message = "Congrats! You've completed the induction!"
                if response.status_code == 200 and not response.json():
                    message += "Make sure to register your card for 3D printing!"  # noqa: E501

                q_embed = discord.Embed(
                    title="Quiz Finished",
                    description=message,
                    color=discord.Color.green(),
                )

                await self.message.edit(
                    embed=q_embed,
                    view=None,
                    delete_after=60,
                )

            else:
                message = f"You got: {self.num_correct}/{self.num_questions} correct. Please try again!"  # noqa: E501

                q_embed = discord.Embed(
                    title="Quiz Finished",
                    description=message,
                    color=discord.Color.red(),
                )

                await self.message.edit(
                    embed=q_embed,
                    view=QuizReset(self.reset),
                    delete_after=60,
                )
            return

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
            )

        self.index += 1


async def launch_quiz(interaction: discord.Interaction):
    quiz = Quiz(interaction=interaction)
    return await quiz.send_next_question()
