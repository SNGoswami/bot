"""Persist per-user lesson progress."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROGRESS_FILE = DATA_DIR / "progress.json"


def _load() -> dict[str, int]:
    if not PROGRESS_FILE.exists():
        return {}
    try:
        with PROGRESS_FILE.open(encoding="utf-8") as f:
            raw = json.load(f)
        return {str(k): int(v) for k, v in raw.items()}
    except (json.JSONDecodeError, OSError, ValueError):
        return {}


def _save(data: dict[str, int]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_lesson_index(user_id: int) -> int:
    return _load().get(str(user_id), 0)


def set_lesson_index(user_id: int, index: int) -> None:
    data = _load()
    data[str(user_id)] = index
    _save(data)


def advance(user_id: int, total_lessons: int) -> int:
    current = get_lesson_index(user_id)
    if current < total_lessons - 1:
        current += 1
        set_lesson_index(user_id, current)
    return current


def reset(user_id: int) -> None:
    set_lesson_index(user_id, 0)
