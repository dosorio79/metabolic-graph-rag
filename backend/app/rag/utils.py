"""Shared utility helpers for RAG runtime modules."""

from __future__ import annotations


def normalize_question(value: str) -> str:
    """Normalize user questions for deterministic parsing.

    - Trims leading/trailing whitespace.
    - Collapses internal whitespace.
    - Lowercases for rule-based matching.
    """
    return " ".join(value.split()).strip().lower()

