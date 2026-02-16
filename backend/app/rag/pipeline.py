"""End-to-end RAG orchestration pipeline."""

from __future__ import annotations

from backend.app.rag.context_builder import build_context
from backend.app.rag.llm_client import generate_answer
from backend.app.rag.query_understanding import classify_question
from backend.app.rag.retriever import retrieve_graph_context
from backend.app.schemas.rag import RAGRequest, RAGResponse, RAGTrace


def run_rag_pipeline(request: RAGRequest) -> RAGResponse:
    """Run deterministic Task 3 pipeline stages with current boilerplate."""
    interpretation = classify_question(request.question)
    retrieved = retrieve_graph_context(interpretation)
    context = build_context(retrieved)
    answer = generate_answer(request.question, context)
    return RAGResponse(
        answer=answer,
        interpretation=interpretation,
        context=context,
        reactions=[],
        compounds=[],
        enzymes=[],
        trace=RAGTrace(),
    )

