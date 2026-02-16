"""Name normalization helpers for API responses."""

from __future__ import annotations


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split()).strip().rstrip(";").strip()
    return cleaned or None


def normalize_name_fields(value):
    if isinstance(value, dict):
        normalized: dict = {}
        for key, item in value.items():
            if key == "name" or key.endswith("_name"):
                normalized[key] = normalize_name(item if isinstance(item, str) else None)
            else:
                normalized[key] = normalize_name_fields(item)
        return normalized
    if isinstance(value, list):
        return [normalize_name_fields(item) for item in value]
    return value
