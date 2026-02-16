"""Name normalization helpers for ingestion."""

from __future__ import annotations


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split()).strip().rstrip(";").strip()
    return cleaned or None
