"""Giskard-compatible wrappers around the backend RAG pipeline."""

from __future__ import annotations

from backend.app.rag.llm_client import get_prompt_versions
from backend.app.rag.pipeline import run_rag_pipeline
from backend.app.schemas.rag import RAGRequest


def rag_predict(question: str) -> str:
    """Return a plain-text answer for a single question."""
    response = run_rag_pipeline(RAGRequest(question=question))
    return response.answer


def rag_predict_with_trace(question: str) -> dict[str, object]:
    """Return answer plus retrieval trace data required by grounding validators."""
    response = run_rag_pipeline(RAGRequest(question=question))
    prompt_versions = get_prompt_versions()
    return {
        "question": question,
        "answer": response.answer,
        "prompt_versions": prompt_versions,
        **prompt_versions,
        "retrieved_reactions": [item.reaction_id for item in response.reactions],
        "retrieved_compounds": [item.compound_id for item in response.compounds],
        "retrieved_enzymes": list(response.enzymes),
        "context": response.context or "",
    }
