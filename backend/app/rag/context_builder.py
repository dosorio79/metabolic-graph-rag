"""Context builder for converting graph data into LLM-ready text."""

from __future__ import annotations


def build_context(retrieved: dict) -> str:
    """Build concise context text from structured graph retrieval output."""
    reactions = retrieved.get("reactions", [])
    compounds = retrieved.get("compounds", [])
    enzymes = retrieved.get("enzymes", [])
    return (
        "Retrieved graph context:\n"
        f"- reactions: {len(reactions)}\n"
        f"- compounds: {len(compounds)}\n"
        f"- enzymes: {len(enzymes)}"
    )

