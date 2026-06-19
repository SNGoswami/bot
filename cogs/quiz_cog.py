"""Quiz command with button answers."""

from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed, QUIZ_COLOR, ERROR_COLOR
from utils.knowledge import quiz_questions

LABELS = ["A", "B", "C", "D"]


class QuizAnswerView(discord.ui.View):
    def __init__(self, question: dict) -> None:
        super().__init__(timeout=120)
        self.question = question
        self.answered = False
        for i, option in enumerate(question["options"][:4]):
            label = f"{LABELS[i]}. {option[:70]}"
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, custom_id=str(i))
            button.callback = self._make_callback(i)
            self.add_item(button)

    def _make_callback(self, index: int):
        async def callback(interaction: discord.Interaction) -> None:
            if self.answered:
                await interaction.response.defer()
                return
            self.answered = True
            for child in self.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True

            correct = self.question["answer"]
            is_correct = index == correct
            color = QUIZ_COLOR if is_correct else ERROR_COLOR
            emoji = "✅" if is_correct else "❌"
            correct_label = self.question["options"][correct]

            embed = mentor_embed(
                title=f"{emoji} {'Correct!' if is_correct else 'Not quite'}",
                description=self.question.get("explanation", ""),
                color=color,
            )
            embed.add_field(name="Correct answer", value=f"**{LABELS[correct]}.** {correct_label}", inline=False)
            await interaction.response.edit_message(embed=embed, view=self)

        return callback


class QuizCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="quiz", description="Test your ESG Saathi architecture knowledge")
    async def quiz(self, interaction: discord.Interaction) -> None:
        questions = quiz_questions()
        if not questions:
            await interaction.response.send_message("No quiz questions loaded.", ephemeral=True)
            return

        q = random.choice(questions)
        options_text = "\n".join(
            f"**{LABELS[i]}.** {opt}" for i, opt in enumerate(q["options"])
        )
        embed = mentor_embed(
            title="🧠 Quick quiz",
            description=f"{q['question']}\n\n{options_text}",
            color=QUIZ_COLOR,
        )
        embed.set_footer(text="Click a button to answer · ESG Saathi Mentor")
        await interaction.response.send_message(embed=embed, view=QuizAnswerView(q))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QuizCog(bot))
