"""Graph retrieval helpers for Task 3 RAG pipeline."""

from __future__ import annotations

from backend.app.schemas.rag import RAGInterpretation


def retrieve_graph_context(interpretation: RAGInterpretation) -> dict:
    """Retrieve structured graph data from Neo4j for a parsed interpretation."""
    return {
        "interpretation": interpretation.model_dump(),
        "reactions": [],
        "compounds": [],
        "enzymes": [],
    }

