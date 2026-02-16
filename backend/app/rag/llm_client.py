"""Thin LLM client wrapper for Task 3.

Current implementation is a deterministic fallback placeholder.
"""

from __future__ import annotations

from backend.app.rag.utils import normalize_question


def generate_answer(question: str, context: str) -> str:
    """Generate a grounded answer from question + context."""
    return (
        "RAG pipeline placeholder answer. "
        f"Question: {normalize_question(question)} | Context length: {len(context)}"
    )
