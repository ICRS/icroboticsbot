from dataclasses import dataclass
from typing import List
import discord
from discord.ui import View, Select

import random


@dataclass
class Question:
    question: str
    correct_options: List[str]
    incorrect_options: List[str]


questions: List[Question] = [
    Question("Hello There?", ["yes"], ["no"]),
    Question("1 + 1", ["2", "two"], ["one", "1"]),
]


class QuizSelectList(Select):
    def __init__(
            self,
            correct_options: List[str],
            incorrect_options: List[str],
            return_callback=lambda x: None,
            **kwargs):
        super().__init__(
            min_values=1,
            max_values=len(incorrect_options) + len(correct_options),
            **kwargs)

        self.correct_options = correct_options
        self.incorrect_options = incorrect_options

        options = self.incorrect_options + self.correct_options
        random.shuffle(options)

        for option in options:
            self.add_option(label=option, value=option, )

        self.return_callback = return_callback

    async def callback(self, interaction):
        print(interaction.data.values())
        v = interaction.data.values().mapping
        v = v.get("values", [])

        correct = (set(self.correct_options) == set(v))
        print(set(self.correct_options).intersection(set(v)))
        await interaction.response.defer()
        await self.return_callback(correct)


class QuizQuestion(View):
    def __init__(
            self,
            correct_options: List[str],
            incorrect_options: List[str],
            return_callback,
            *, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.add_item(
            QuizSelectList(
                correct_options,
                incorrect_options,
                return_callback=return_callback))


class Quiz:
    def __init__(self, interaction: discord.Interaction) -> None:
        self.questions = questions
        self.index = 0
        self.num_questions = len(self.questions)

        self.num_correct = 0
        self.interaction = interaction

        self.message: discord.Message | None = None

    async def question_callback(self, correct: bool):
        self.num_correct += correct
        print(self.num_correct)
        await self.send_next_question()

    async def send_next_question(self):
        if self.index >= self.num_questions:
            await self.message.edit(
                content=f"Done: Num correct {self.num_correct}/{self.num_questions}",
                embed=None,
                view=None)
            return

        q = self.questions[self.index]
        question = QuizQuestion(
            q.correct_options,
            q.incorrect_options,
            return_callback=self.question_callback
        )
        q_embed = discord.Embed(
            title=f"Question {self.index + 1}",
            description=q.question,
            color=discord.Color.green(),
        )

        if not self.index:
            await self.interaction.response.defer()
            self.message: discord.Message | None = await self.interaction.followup.send(
                embed=q_embed,
                view=question,
                ephemeral=True
            )
        else:
            assert self.message is not None
            await self.message.edit(
                embed=q_embed,
                view=question,
            )

        self.index += 1


async def launch_quiz(interaction: discord.Interaction):
    quiz = Quiz(interaction=interaction)
    return await quiz.send_next_question()
