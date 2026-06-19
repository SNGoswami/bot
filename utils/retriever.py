"""Simple keyword RAG over bot/knowledge/ (no vector DB)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from utils.knowledge import KNOWLEDGE

STOPWORDS = frozenset(
    """
    a an the and or but in on at to for of is are was were be been being
    it this that these those i you we they he she what which who how when where
    why does do did can could should would will with from about into our your
    me my tell explain describe
    """.split()
)

MAX_CHUNK_CHARS = 2200
TOP_K = 5


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    score: float
    text: str


def _tokenize(query: str) -> list[str]:
    words = re.findall(r"[a-z0-9_./-]+", query.lower())
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]


def _knowledge_files() -> list[Path]:
    patterns = ("**/*.md", "**/*.yaml", "**/*.yml", "**/*.json")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(KNOWLEDGE.glob(pattern))
    return sorted({p.resolve() for p in files if p.is_file()})


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _score_text(text: str, tokens: list[str], source: str) -> float:
    if not tokens:
        return 0.0
    lower = text.lower()
    source_lower = source.lower()
    score = 0.0
    for token in tokens:
        count = lower.count(token)
        if count:
            score += count * (2.0 if len(token) > 4 else 1.0)
        if token in source_lower:
            score += 3.0
    return score


def retrieve(query: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    tokens = _tokenize(query)
    if not tokens:
        return []

    ranked: list[RetrievedChunk] = []
    for path in _knowledge_files():
        rel = str(path.relative_to(KNOWLEDGE.parent))
        text = _read_file(path)
        if not text.strip():
            continue
        score = _score_text(text, tokens, rel)
        if score <= 0:
            continue
        excerpt = text if len(text) <= MAX_CHUNK_CHARS else text[:MAX_CHUNK_CHARS] + "\n…"
        ranked.append(RetrievedChunk(source=rel, score=score, text=excerpt))

    ranked.sort(key=lambda c: c.score, reverse=True)
    return ranked[:top_k]


def format_context(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return ""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"### Source {i}: `{chunk.source}`\n{chunk.text}")
    return "\n\n".join(parts)
