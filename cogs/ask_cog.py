"""Grounded /ask — keyword RAG + Claude."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed, truncate, ERROR_COLOR
from utils.llm import ask_mentor
from utils.retriever import format_context, retrieve


class AskCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="ask",
        description="Ask about ESG Saathi architecture (knowledge base + Claude)",
    )
    @app_commands.describe(question="e.g. How does JWT auth work? Where is Lighthouse scoring?")
    async def ask(self, interaction: discord.Interaction, question: str) -> None:
        question = question.strip()
        if len(question) < 5:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Question too short",
                    description="Please ask a fuller question (at least 5 characters).",
                    color=ERROR_COLOR,
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)

        chunks = retrieve(question)
        context = format_context(chunks)

        try:
            answer = await ask_mentor(question, context)
        except RuntimeError as exc:
            await interaction.followup.send(
                embed=mentor_embed(title="LLM not configured", description=str(exc), color=ERROR_COLOR),
                ephemeral=True,
            )
            return
        except Exception as exc:
            await interaction.followup.send(
                embed=mentor_embed(
                    title="Could not get an answer",
                    description=f"Claude request failed: `{exc}`\n\nTry `/where`, `/schema`, or `/trace` instead.",
                    color=ERROR_COLOR,
                ),
                ephemeral=True,
            )
            return

        sources = ", ".join(f"`{c.source}`" for c in chunks[:3]) if chunks else "_none matched_"
        embed = mentor_embed(
            title="💬 Mentor answer",
            description=truncate(answer, 3900),
            fields=[
                ("Your question", question[:256], False),
                ("Sources used", sources, False),
            ],
        )
        embed.set_footer(text="Grounded in knowledge/ · verify with /where /schema /trace")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AskCog(bot))
