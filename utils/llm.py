"""Anthropic Claude client for grounded /ask answers."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_MODEL = "claude-sonnet-4-20250514"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

SYSTEM_PROMPT = """You are Saathi Mentor, an internal knowledge-transfer assistant for the ESG Saathi engineering team.

Rules:
- Answer ONLY using the provided CONTEXT about architecture, infrastructure, code locations, database schema, and request flows.
- If CONTEXT is insufficient, say clearly that you do not have enough information in the knowledge base.
- Suggest structured commands when helpful: /where, /schema, /trace, /learn, /topic, /link, /api.
- Never invent file paths, table names, API endpoints, or ports not present in CONTEXT.
- Never output secrets, credentials, API keys, passwords, or webhook URLs.
- Be concise and practical. Use bullet points for lists. Put paths and table names in backticks.
- You are teaching engineers onboarding to the codebase — tone is helpful and precise."""


def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return key or None


def get_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _extract_text(payload: dict[str, Any]) -> str:
    blocks = payload.get("content") or []
    for block in blocks:
        if block.get("type") == "text":
            text = (block.get("text") or "").strip()
            if text:
                return text
    raise ValueError("Claude returned no text content")


async def ask_mentor(question: str, context: str) -> str:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file to use /ask."
        )

    if not context.strip():
        return (
            "I couldn't find relevant snippets in the knowledge base for that question. "
            "Try `/where <feature>`, `/schema <table>`, `/topic <name>`, or rephrase with "
            "terms like `lighthouse`, `auth`, `clients`, or `brsr`."
        )

    user_prompt = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer the question using CONTEXT only."
    )

    body = {
        "model": get_model(),
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": API_VERSION,
                "content-type": "application/json",
            },
            json=body,
        )
        response.raise_for_status()
        return _extract_text(response.json())
