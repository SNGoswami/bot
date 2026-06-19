"""Guided curriculum: /learn and /topic."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed, truncate
from utils.knowledge import curriculum, lesson_by_index, lesson_content, lesson_index_by_id, topic_aliases
from utils import progress as progress_store


class LearnCog(commands.Cog):
    learn = app_commands.Group(name="learn", description="Guided onboarding curriculum")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _send_lesson(self, interaction: discord.Interaction, index: int) -> None:
        lessons = curriculum()
        lesson = lesson_by_index(index)
        if not lesson:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Curriculum complete",
                    description="You've finished all lessons. Run `/quiz` or `/trace list` to practice.",
                ),
                ephemeral=True,
            )
            return

        content = lesson_content(lesson["id"]) or lesson.get("summary", "")
        body = truncate(
            f"**Lesson {index + 1}/{len(lessons)}:** {lesson['title']}\n"
            f"_{lesson.get('summary', '')}_\n\n{content}"
        )
        embed = mentor_embed(title=f"📘 {lesson['title']}", description=body)
        embed.add_field(
            name="Continue",
            value="`/learn next` · `/learn progress` · `/help learn`",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @learn.command(name="start", description="Start or resume the onboarding curriculum")
    async def learn_start(self, interaction: discord.Interaction) -> None:
        index = progress_store.get_lesson_index(interaction.user.id)
        await self._send_lesson(interaction, index)

    @learn.command(name="next", description="Go to the next lesson")
    async def learn_next(self, interaction: discord.Interaction) -> None:
        total = len(curriculum())
        index = progress_store.advance(interaction.user.id, total)
        await self._send_lesson(interaction, index)

    @learn.command(name="progress", description="Show your current lesson progress")
    async def learn_progress(self, interaction: discord.Interaction) -> None:
        lessons = curriculum()
        index = progress_store.get_lesson_index(interaction.user.id)
        lesson = lesson_by_index(index)
        title = lesson["title"] if lesson else "Complete"
        await interaction.response.send_message(
            embed=mentor_embed(
                title="Your progress",
                description=(
                    f"**Lesson {index + 1} of {len(lessons)}:** {title}\n\n"
                    f"`/learn start` to read current lesson · `/learn next` to advance"
                ),
            ),
            ephemeral=True,
        )

    @learn.command(name="reset", description="Restart from lesson 1")
    async def learn_reset(self, interaction: discord.Interaction) -> None:
        progress_store.reset(interaction.user.id)
        await interaction.response.send_message(
            embed=mentor_embed(
                title="Progress reset",
                description="You're back at lesson 1. Run `/learn start`.",
            ),
            ephemeral=True,
        )

    @app_commands.command(name="topic", description="Jump to a curriculum topic")
    @app_commands.describe(name="e.g. auth, database, lighthouse, infra")
    async def topic(self, interaction: discord.Interaction, name: str) -> None:
        aliases = topic_aliases()
        key = name.lower().strip()
        lesson_id = aliases.get(key)
        if not lesson_id:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Topic not found",
                    description=f"Try: `{', '.join(sorted(set(aliases.keys())))}`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        index = lesson_index_by_id(lesson_id)
        if index is None:
            await interaction.response.send_message("Lesson not found.", ephemeral=True)
            return

        progress_store.set_lesson_index(interaction.user.id, index)
        await self._send_lesson(interaction, index)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LearnCog(bot))
