"""Discord embed helpers for Saathi Mentor."""

from __future__ import annotations

import discord

from utils.knowledge import docs_version

MENTOR_COLOR = 0x0D9488
ERROR_COLOR = 0xDC2626
QUIZ_COLOR = 0x2563EB


def mentor_embed(
    *,
    title: str,
    description: str | None = None,
    fields: list[tuple[str, str, bool]] | None = None,
    color: int = MENTOR_COLOR,
) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value[:1024], inline=inline)
    embed.set_footer(text=f"ESG Saathi Mentor · docs {docs_version()}")
    return embed


def truncate(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
