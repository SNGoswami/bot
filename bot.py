"""ESG Saathi Mentor — Discord KT bot for architecture, infra, schema, and code paths."""

from __future__ import annotations

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

COGS = [
    "cogs.help_cog",
    "cogs.learn_cog",
    "cogs.lookup_cog",
    "cogs.trace_cog",
    "cogs.quiz_cog",
    "cogs.ask_cog",
]

intents = discord.Intents.default()
intents.message_content = True


class SaathiMentorBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension(cog)

    async def on_ready(self) -> None:
        synced = await self.tree.sync()
        print(f"Saathi Mentor logged in as {self.user} (id={self.user.id})")
        print(f"Synced {len(synced)} slash command(s)")


def main() -> None:
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN environment variable is required")
    bot = SaathiMentorBot()
    bot.run(token)


if __name__ == "__main__":
    main()
