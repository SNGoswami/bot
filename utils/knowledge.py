"""Load and query the Saathi Mentor knowledge base."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "knowledge"


@lru_cache(maxsize=1)
def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def curriculum() -> list[dict[str, Any]]:
    data = _load_yaml(KNOWLEDGE / "curriculum.yaml")
    return data.get("lessons", [])


def lesson_content(lesson_id: str) -> str | None:
    for lesson in curriculum():
        if lesson["id"] == lesson_id:
            path = KNOWLEDGE / lesson["file"]
            if path.exists():
                return path.read_text(encoding="utf-8")
    return None


def lesson_by_index(index: int) -> dict[str, Any] | None:
    lessons = curriculum()
    if 0 <= index < len(lessons):
        return lessons[index]
    return None


def lesson_index_by_id(lesson_id: str) -> int | None:
    for i, lesson in enumerate(curriculum()):
        if lesson["id"] == lesson_id:
            return i
    return None


def topic_aliases() -> dict[str, str]:
    return {
        "topology": "01-topology",
        "auth": "02-auth",
        "session": "02-auth",
        "ui": "03-ui-modules",
        "ui-modules": "03-ui-modules",
        "backend": "04-backend",
        "database": "05-database",
        "db": "05-database",
        "schema": "05-database",
        "lighthouse": "06-lighthouse",
        "brsr": "07-brsr",
        "infra": "08-infra",
        "infrastructure": "08-infra",
        "ops": "08-infra",
    }


@lru_cache(maxsize=1)
def features() -> dict[str, Any]:
    return _load_yaml(KNOWLEDGE / "lookups" / "features.yaml").get("features", {})


def find_feature(query: str) -> tuple[str, dict[str, Any]] | None:
    key = query.lower().strip().replace(" ", "-").replace("_", "-")
    all_features = features()
    if key in all_features:
        return key, all_features[key]
    for name, data in all_features.items():
        if key in name or key in data.get("name", "").lower():
            return name, data
    return None


@lru_cache(maxsize=1)
def schemas() -> dict[str, Any]:
    return _load_yaml(KNOWLEDGE / "lookups" / "schema.yaml").get("tables", {})


def find_table(query: str) -> tuple[str, dict[str, Any]] | None:
    key = query.lower().strip().replace("-", "_")
    all_tables = schemas()
    if key in all_tables:
        return key, all_tables[key]
    for name, data in all_tables.items():
        if key in name:
            return name, data
    return None


@lru_cache(maxsize=1)
def apis() -> dict[str, Any]:
    return _load_yaml(KNOWLEDGE / "lookups" / "apis.yaml").get("endpoints", {})


def find_api(path: str) -> tuple[str, dict[str, Any]] | None:
    normalized = path.strip()
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    all_apis = apis()
    if normalized in all_apis:
        return normalized, all_apis[normalized]
    for endpoint, data in all_apis.items():
        if normalized in endpoint or endpoint in normalized:
            return endpoint, data
    return None


@lru_cache(maxsize=1)
def linkages() -> list[dict[str, Any]]:
    return _load_yaml(KNOWLEDGE / "lookups" / "linkages.yaml").get("linkages", [])


def find_linkage(from_entity: str, to_entity: str) -> dict[str, Any] | None:
    f = from_entity.lower().strip().rstrip("s")
    t = to_entity.lower().strip().rstrip("s")
    for link in linkages():
        from_name = link["from"].lower().rstrip("s")
        to_name = link["to"].lower().rstrip("s")
        if f in from_name and t in to_name:
            return link
    return None


@lru_cache(maxsize=1)
def glossary() -> dict[str, str]:
    return _load_yaml(KNOWLEDGE / "lookups" / "glossary.yaml").get("terms", {})


def find_term(query: str) -> tuple[str, str] | None:
    terms = glossary()
    key = query.strip()
    if key in terms:
        return key, terms[key]
    lower = key.lower()
    for term, definition in terms.items():
        if lower == term.lower():
            return term, definition
    return None


def list_traces() -> list[dict[str, Any]]:
    traces_dir = KNOWLEDGE / "traces"
    result = []
    for path in sorted(traces_dir.glob("*.yaml")):
        data = _load_yaml(path)
        result.append(data)
    return result


def find_trace(trace_id: str) -> dict[str, Any] | None:
    key = trace_id.lower().strip()
    for trace in list_traces():
        if trace.get("id", "").lower() == key:
            return trace
        if key in trace.get("name", "").lower():
            return trace
    return None


def quiz_questions() -> list[dict[str, Any]]:
    path = KNOWLEDGE / "quizzes" / "general.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", [])


def docs_version() -> str:
    return "2026-06-19"
