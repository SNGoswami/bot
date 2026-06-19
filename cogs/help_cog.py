"""Help and onboarding guide for Saathi Mentor."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed
from utils.knowledge import curriculum, list_traces


class HelpCog(commands.Cog):
    SECTIONS = {
        "overview": (
            "Saathi Mentor — ESG Saathi KT bot",
            (
                "I'm your **teacher/mentor** for ESG Saathi architecture, infra, code locations, "
                "database schema, and request flows.\n\n"
                "**Quick start**\n"
                "1. `/learn start` — begin the 8-lesson onboarding track\n"
                "2. `/where lighthouse` — find UI + backend paths for a feature\n"
                "3. `/trace lighthouse-submit` — walk through a request end-to-end\n"
                "4. `/ask <question>` — free-form questions (Gemini + knowledge base)\n"
                "5. `/quiz` — test your knowledge\n\n"
                "**All sections:** `/help learn` · `/help lookup` · `/help trace` · `/help ask` · `/help quiz`\n"
                "**Progress:** `/learn progress` · **Jump to topic:** `/topic database`"
            ),
        ),
        "learn": (
            "Learning commands",
            (
                "`/learn start` — Lesson 1 (or resume where you left off)\n"
                "`/learn next` — Advance to the next lesson\n"
                "`/learn progress` — Your current lesson (e.g. 3/8)\n"
                "`/learn reset` — Restart from lesson 1\n"
                "`/topic <name>` — Jump to a topic (`auth`, `database`, `lighthouse`, …)\n\n"
                "**Curriculum (8 lessons)**\n"
                + "\n".join(f"• {i + 1}. {l['title']}" for i, l in enumerate(curriculum()))
            ),
        ),
        "lookup": (
            "Lookup commands",
            (
                "`/where <feature>` — Code locations for a domain\n"
                "  e.g. `lighthouse`, `brsr`, `scope3`, `auth`, `clients`\n\n"
                "`/schema <table>` — Table columns and foreign keys\n"
                "  e.g. `clients`, `lighthouse_assessments`, `users`\n\n"
                "`/api <path>` — Endpoint details\n"
                "  e.g. `/api/lighthouse/submit`\n\n"
                "`/link <from> <to>` — How entities connect\n"
                "  e.g. `client brsr`, `users clients`\n\n"
                "`/glossary <term>` — Define BRSR, Lighthouse, apiFetch, …"
            ),
        ),
        "trace": (
            "Trace commands",
            (
                "`/trace list` — Available request flows\n"
                "`/trace <flow>` — Step-by-step walkthrough with buttons\n\n"
                "**Available flows**\n"
                + "\n".join(f"• `{t['id']}` — {t['name']}" for t in list_traces())
                + "\n\n"
                "Use **Previous** / **Next** buttons to navigate steps."
            ),
        ),
        "ask": (
            "Ask command (LLM)",
            (
                "`/ask <question>` — Natural-language questions about the codebase\n\n"
                "**How it works**\n"
                "1. Keyword search over `knowledge/` (lessons, lookups, traces)\n"
                "2. Top snippets sent to **Claude** with strict grounding rules\n"
                "3. Answer cites paths from context only\n\n"
                "**Examples**\n"
                "• `How does JWT auth work in ESG Saathi?`\n"
                "• `Where is Lighthouse scoring implemented?`\n"
                "• `How are clients linked to BRSR assessments?`\n\n"
                "**Setup:** set `ANTHROPIC_API_KEY` in `.env` (optional `ANTHROPIC_MODEL`)\n\n"
                "For exact facts, prefer `/where`, `/schema`, `/trace` — they are rule-based and always accurate."
            ),
        ),
        "quiz": (
            "Quiz command",
            (
                "`/quiz` — Random multiple-choice question from the knowledge base\n\n"
                "Click a button to answer. You'll get immediate feedback with an explanation.\n"
                "Great after finishing `/learn next` a few times."
            ),
        ),
    }

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Guide to Saathi Mentor commands and learning paths")
    @app_commands.describe(section="Optional: overview, learn, lookup, trace, ask, quiz")
    async def help_command(
        self,
        interaction: discord.Interaction,
        section: str | None = None,
    ) -> None:
        key = (section or "overview").lower().strip()
        if key not in self.SECTIONS:
            valid = ", ".join(self.SECTIONS)
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Unknown help section",
                    description=f"Try: `{valid}`\n\nExample: `/help learn`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        title, body = self.SECTIONS[key]
        await interaction.response.send_message(embed=mentor_embed(title=title, description=body))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
