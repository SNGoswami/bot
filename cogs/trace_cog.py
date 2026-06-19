"""Interactive request-flow traces."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed
from utils.knowledge import find_trace, list_traces


class TraceStepView(discord.ui.View):
    def __init__(self, trace: dict, step_index: int = 0) -> None:
        super().__init__(timeout=300)
        self.trace = trace
        self.step_index = step_index
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        steps = self.trace.get("steps", [])
        self.prev_button.disabled = self.step_index <= 0
        self.next_button.disabled = self.step_index >= len(steps) - 1

    def _build_embed(self) -> discord.Embed:
        steps = self.trace.get("steps", [])
        step = steps[self.step_index]
        total = len(steps)
        fields = [
            ("Layer", step.get("layer", "—"), True),
            ("File", f"`{step.get('file', '—')}`", False),
            ("Action", step.get("action", "—"), False),
        ]
        if self.trace.get("roles"):
            fields.insert(0, ("Roles", ", ".join(self.trace["roles"]), True))
        if self.trace.get("tables"):
            fields.append(("Tables", ", ".join(f"`{t}`" for t in self.trace["tables"]), True))

        return mentor_embed(
            title=f"🔍 {self.trace.get('name', 'Trace')} — Step {self.step_index + 1}/{total}",
            description=f"**{step.get('title', step.get('layer', 'Step'))}**",
            fields=fields,
        )

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.step_index > 0:
            self.step_index -= 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        steps = self.trace.get("steps", [])
        if self.step_index < len(steps) - 1:
            self.step_index += 1
        self._sync_buttons()
        await interaction.response.edit_message(embed=self._build_embed(), view=self)


class TraceCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="trace", description="Walk through a request flow step by step")
    @app_commands.describe(flow="Flow id or 'list' — e.g. lighthouse-submit, login-otp")
    async def trace(self, interaction: discord.Interaction, flow: str) -> None:
        if flow.lower().strip() == "list":
            lines = "\n".join(
                f"• `{t['id']}` — {t.get('description', t.get('name', ''))}"
                for t in list_traces()
            )
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Available traces",
                    description=lines + "\n\nUsage: `/trace lighthouse-submit`",
                )
            )
            return

        data = find_trace(flow)
        if not data:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Trace not found",
                    description="Run `/trace list` to see available flows.",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        view = TraceStepView(data, 0)
        await interaction.response.send_message(embed=view._build_embed(), view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TraceCog(bot))
