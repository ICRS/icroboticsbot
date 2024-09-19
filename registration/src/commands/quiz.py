from dataclasses import dataclass, field
from typing import List
from discord.ui import View, Select
import os


import discord
import random
import requests
from src.utils import *

from src.commands.stats import SERVER_IP

DATABASE_ADAPTER_IP = os.getenv("SERVER_IP")
result = requests.get(SERVER_IP + "/induction/quiz")
questions = result.json()


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


def parse_questions(questions):
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


questions: List[Question] = parse_questions(questions)


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
    def __init__(self, interaction: discord.Interaction, shortcode: str) -> None:
        self.questions = questions
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
            response = requests.post(
            SERVER_IP + "/induction/induct/discord-id",
                params={"id": str(self.user_id)})

            roleWorked = await addRoletoUser(self.interaction, self.shortcode, self.member)

            if response.status_code == 200 and roleWorked:
                message = "Congrats! You've completed the induction!\n\n"
                message += "If this is your first year  in ICRS please\n"  # noqa: E501
                message += "**Register your card in person** for 3D printing and door access!\n\n"  # noqa: E501
                message += "Also check out our Insta: [linktr.ee/icrobotics](https://linktr.ee/icrobotics)"  # noqa: E501


                q_embed = discord.Embed(
                    title="Quiz Passed!",
                    description=message,
                    color=discord.Color.green(),
                )

            elif not(roleWorked):
                q_embed = discord.Embed(
                    title="Quiz Semi Worked!",
                    description="Server error, Quiz Semi Worked but the adding the discord role didn't. You DID pass the quiz! Please show committee a screenshot of this message",
                    color=discord.Color.red()
                )

            else:
                q_embed = discord.Embed(
                    title="Error but Passed!",
                    description="Server error, but you DID pass the quiz! Please show committee a screenshot of this message",
                    color=discord.Color.red()
                )

            await self.message.edit(
                embed=q_embed,
                view=None,
            )

        else:
            print(self.incorrect_ind)
            message = f"You got: {self.num_correct}/{self.num_questions} correct. Please try again!\n\n"  # noqa: E501
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


async def addRoletoUser(interaction: discord.Interaction, shortcode: str, member):
    role = discord.utils.get(
        interaction.guild.roles, name="Verified Member")

    result = requests.post(
        DATABASE_ADAPTER_IP + "/discord-id/register",
        params={
            "shortcode": shortcode.strip().lower(),
            "discord_id": str(member.id)
        })

    if result.status_code == 401:
        return await interaction.response.send_message(
            embed=user_not_member_msg(), ephemeral=True)
    elif result.status_code == 304:
        return await interaction.response.send_message(
            embed=code_already_used_msg(), ephemeral=True)
    elif result.status_code == 422:
        return await interaction.response.send_message(
            embed=how_to_msg(), ephemeral=True
        )
    elif result.status_code != 200:
        return await interaction.response.send_message(
            embed=error_msg("Something went wrong on the server!"),
        )
    await member.add_roles(
        role, reason="Membership verified using API")

    return True