"""Rule-based query understanding utilities for Task 3 RAG pipeline."""

from __future__ import annotations

from backend.app.schemas.rag import RAGInterpretation
from backend.app.rag.utils import normalize_question


def classify_question(question: str) -> RAGInterpretation:
    """Classify a user question into an initial interpretation skeleton.

    Task 3 Step 1 should keep this deterministic and rule-based.
    """
    normalized = normalize_question(question)
    if not normalized:
        return RAGInterpretation(entity_type="unknown", intent="unknown", confidence=0.0)
    return RAGInterpretation(entity_type="unknown", intent="unknown", confidence=0.0)
