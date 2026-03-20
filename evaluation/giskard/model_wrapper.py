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
    interpretation = response.interpretation
    retrieval_empty = not (response.reactions or response.compounds or response.enzymes)
    return {
        "question": question,
        "answer": response.answer,
        "prompt_versions": prompt_versions,
        **prompt_versions,
        "interpretation": {
            "entity_type": interpretation.entity_type,
            "entity_id": interpretation.entity_id,
            "entity_name": interpretation.entity_name,
            "intent": interpretation.intent,
            "confidence": interpretation.confidence,
        },
        "retrieved_reactions": [item.reaction_id for item in response.reactions],
        "retrieved_compounds": [item.compound_id for item in response.compounds],
        "retrieved_enzymes": list(response.enzymes),
        "trace_pathway_ids": list(response.trace.pathway_ids),
        "trace_reaction_ids": list(response.trace.reaction_ids),
        "trace_compound_ids": list(response.trace.compound_ids),
        "trace_enzyme_ecs": list(response.trace.enzyme_ecs),
        "retrieval_empty": retrieval_empty,
        "context": response.context or "",
    }
