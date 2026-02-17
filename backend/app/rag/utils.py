"""Shared utility helpers for RAG runtime modules."""

from __future__ import annotations

from typing import Any, Mapping


def normalize_question(value: str) -> str:
    """Normalize user questions for deterministic parsing.

    - Trims leading/trailing whitespace.
    - Collapses internal whitespace.
    - Lowercases for rule-based matching.
    """
    return " ".join(value.split()).strip().lower()


def format_classification_debug(debug: Mapping[str, Any]) -> str:
    """Format query-understanding rule trace payload for logs/inspection."""
    ordered_keys = (
        "normalized_question",
        "intent_before_promotion",
        "intent_after_promotion",
        "matched_intent_rule",
        "entity_type_from_id",
        "entity_id_from_id",
        "hinted_entity_type",
        "extracted_entity_name",
        "matched_name_rule",
        "resolved_entity_type",
        "fallback_applied",
        "confidence",
    )
    lines = ["Query understanding debug:"]
    for key in ordered_keys:
        lines.append(f"- {key}: {debug.get(key)}")
    return "\n".join(lines)
