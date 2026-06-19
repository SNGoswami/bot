"""Anthropic Claude client for grounded /ask answers."""

from __future__ import annotations

import os
from typing import Any

import httpx

# Widely available models first — Claude 4.x may not be enabled on every API key.
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
FALLBACK_MODELS = (
    "claude-3-5-haiku-20241022",
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
)
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
MAX_CONTEXT_CHARS = 20_000

SYSTEM_PROMPT = """You are Saathi Mentor, an internal knowledge-transfer assistant for the ESG Saathi engineering team.

Rules:
- Answer ONLY using the provided CONTEXT about architecture, infrastructure, code locations, database schema, and request flows.
- If CONTEXT is insufficient, say clearly that you do not have enough information in the knowledge base.
- Suggest structured commands when helpful: /where, /schema, /trace, /learn, /topic, /link, /api.
- Never invent file paths, table names, API endpoints, or ports not present in CONTEXT.
- Never output secrets, credentials, API keys, passwords, or webhook URLs.
- Be concise and practical. Use bullet points for lists. Put paths and table names in backticks.
- You are teaching engineers onboarding to the codebase — tone is helpful and precise."""


class AnthropicAPIError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'")
    return key or None


def get_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _model_candidates() -> list[str]:
    configured = get_model()
    models: list[str] = []
    for model in (configured, *FALLBACK_MODELS):
        if model and model not in models:
            models.append(model)
    return models


def _extract_text(payload: dict[str, Any]) -> str:
    blocks = payload.get("content") or []
    for block in blocks:
        if block.get("type") == "text":
            text = (block.get("text") or "").strip()
            if text:
                return text
    raise AnthropicAPIError("Claude returned no text content")


def _parse_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
        err = payload.get("error") or {}
        message = err.get("message") or response.text
        err_type = err.get("type")
        if err_type:
            return f"{err_type}: {message}"
        return str(message)
    except Exception:
        return response.text or f"HTTP {response.status_code}"


def _should_try_next_model(status_code: int, detail: str) -> bool:
    if status_code == 404:
        return True
    if status_code != 400:
        return False
    lowered = detail.lower()
    return any(
        token in lowered
        for token in (
            "model",
            "not_found",
            "not found",
            "temperature",
            "unsupported",
            "permission",
            "access",
        )
    )


def _build_body(model: str, user_prompt: str) -> dict[str, Any]:
    # Keep the payload minimal — some models reject optional params (e.g. temperature).
    return {
        "model": model,
        "max_tokens": 2048,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }


async def _call_model(client: httpx.AsyncClient, api_key: str, model: str, user_prompt: str) -> str:
    response = await client.post(
        API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        },
        json=_build_body(model, user_prompt),
    )
    if response.is_success:
        return _extract_text(response.json())

    detail = _parse_error(response)
    raise AnthropicAPIError(
        f"{detail} (model: {model})",
        status_code=response.status_code,
    )


async def ask_mentor(question: str, context: str) -> str:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your environment or .env file to use /ask."
        )
    if not api_key.startswith("sk-ant-"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY looks invalid. It should start with sk-ant-."
        )

    if not context.strip():
        return (
            "I couldn't find relevant snippets in the knowledge base for that question. "
            "Try `/where <feature>`, `/schema <table>`, `/topic <name>`, or rephrase with "
            "terms like `lighthouse`, `auth`, `clients`, or `brsr`."
        )

    clipped_context = context[:MAX_CONTEXT_CHARS]
    if len(context) > MAX_CONTEXT_CHARS:
        clipped_context += "\n…"

    user_prompt = (
        f"CONTEXT:\n{clipped_context}\n\n"
        f"QUESTION:\n{question}\n\n"
        "Answer the question using CONTEXT only."
    )

    errors: list[str] = []
    async with httpx.AsyncClient(timeout=90.0) as client:
        for model in _model_candidates():
            try:
                return await _call_model(client, api_key, model, user_prompt)
            except AnthropicAPIError as exc:
                errors.append(str(exc))
                if exc.status_code and _should_try_next_model(exc.status_code, str(exc)):
                    continue
                raise

    summary = "\n".join(f"• {e}" for e in errors[-3:])
    raise AnthropicAPIError(
        "All configured Claude models failed.\n" + summary,
        status_code=400,
    )
