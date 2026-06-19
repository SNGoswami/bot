"""Lookup commands: where, schema, api, link, glossary."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from utils.embeds import mentor_embed
from utils.knowledge import find_api, find_feature, find_linkage, find_table, find_term, linkages


class LookupCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="where", description="Find UI and backend code locations for a feature")
    @app_commands.describe(feature="e.g. lighthouse, brsr, scope3, auth, clients")
    async def where(self, interaction: discord.Interaction, feature: str) -> None:
        result = find_feature(feature)
        if not result:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Feature not found",
                    description="Try: `lighthouse`, `brsr`, `scope3`, `auth`, `clients`, `workforce`, `ai-advisor`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        key, data = result
        fields = [
            ("Description", data.get("description", "—"), False),
        ]
        if data.get("ui"):
            fields.append(("UI paths", "\n".join(f"`{p}`" for p in data["ui"]), False))
        if data.get("backend"):
            fields.append(("Backend paths", "\n".join(f"`{p}`" for p in data["backend"]), False))
        if data.get("api"):
            fields.append(("API", f"`{data['api']}`", True))
        if data.get("tables"):
            fields.append(("Tables", ", ".join(f"`{t}`" for t in data["tables"]), True))

        await interaction.response.send_message(
            embed=mentor_embed(title=f"📍 {data.get('name', key)}", fields=fields)
        )

    @app_commands.command(name="schema", description="Show database table schema and linkages")
    @app_commands.describe(table="e.g. clients, users, lighthouse_assessments")
    async def schema(self, interaction: discord.Interaction, table: str) -> None:
        result = find_table(table)
        if not result:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Table not found",
                    description="Try: `users`, `clients`, `lighthouse_assessments`, `brsr_assessments`, `workforce_reports`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        name, data = result
        columns = data.get("columns", [])
        refs = data.get("references", [])
        col_text = "\n".join(f"• {c}" for c in columns) if columns else "—"
        ref_text = ", ".join(f"`{r}`" for r in refs) if refs else "—"

        await interaction.response.send_message(
            embed=mentor_embed(
                title=f"🗄️ {name}",
                description=data.get("description", ""),
                fields=[
                    ("Columns", col_text, False),
                    ("References", ref_text, False),
                ],
            )
        )

    @app_commands.command(name="api", description="Look up a Spring API endpoint")
    @app_commands.describe(path="e.g. /api/lighthouse/submit")
    async def api(self, interaction: discord.Interaction, path: str) -> None:
        result = find_api(path)
        if not result:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Endpoint not found",
                    description="Try: `/api/auth/me`, `/api/lighthouse/submit`, `/api/brsr`, `/api/clients`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        endpoint, data = result
        await interaction.response.send_message(
            embed=mentor_embed(
                title=f"🔌 {data.get('method', 'GET')} {endpoint}",
                description=data.get("description", ""),
                fields=[
                    ("Auth", data.get("auth", "—"), True),
                    ("Controller", f"`{data.get('controller', '—')}`", True),
                ],
            )
        )

    @app_commands.command(name="link", description="Show how two entities are linked in the database")
    @app_commands.describe(from_entity="e.g. client", to_entity="e.g. brsr")
    async def link(
        self,
        interaction: discord.Interaction,
        from_entity: str,
        to_entity: str,
    ) -> None:
        result = find_linkage(from_entity, to_entity)
        if not result:
            hints = "\n".join(
                f"• `{l['from']}` → `{l['to']}`" for l in linkages()[:6]
            )
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Linkage not found",
                    description=f"Try one of:\n{hints}",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=mentor_embed(
                title=f"🔗 {result['from']} → {result['to']}",
                fields=[
                    ("Relationship", result.get("relationship", "—"), False),
                    ("Via", f"`{result.get('via', '—')}`", False),
                ],
            )
        )

    @app_commands.command(name="glossary", description="Define an ESG Saathi or architecture term")
    @app_commands.describe(term="e.g. BRSR, Lighthouse, apiFetch")
    async def glossary(self, interaction: discord.Interaction, term: str) -> None:
        result = find_term(term)
        if not result:
            await interaction.response.send_message(
                embed=mentor_embed(
                    title="Term not found",
                    description="Try: `BRSR`, `Lighthouse`, `Scope 3`, `BFF`, `apiFetch`, `viewRegistry`",
                    color=0xDC2626,
                ),
                ephemeral=True,
            )
            return

        name, definition = result
        await interaction.response.send_message(
            embed=mentor_embed(title=f"📖 {name}", description=definition)
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LookupCog(bot))
