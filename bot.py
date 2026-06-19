"""ESG Saathi Mentor — Discord KT bot for architecture, infra, schema, and code paths."""

from __future__ import annotations

import os

import discord
from discord import app_commands
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
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension(cog)

    async def on_ready(self) -> None:
        synced = await self.tree.sync()
        print(f"Saathi Mentor logged in as {self.user} (id={self.user.id})")
        print(f"Synced {len(synced)} slash command(s)")
        for cmd in synced:
            print(f"  - /{cmd.name}")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        print(f"Command error: {error}")
        message = "Something went wrong running that command. Try again in a moment."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


def main() -> None:
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN environment variable is required")
    bot = SaathiMentorBot()
    bot.run(token)


if __name__ == "__main__":
    main()
