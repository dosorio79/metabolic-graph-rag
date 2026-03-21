"""End-to-end RAG orchestration pipeline."""

from __future__ import annotations

from backend.app.rag.context_builder import build_context
from backend.app.rag.llm_client import generate_answer
from backend.app.rag.query_understanding import classify_question
from backend.app.rag.retriever import retrieve_graph_context
from backend.app.schemas.rag import RAGCompoundSummary, RAGEvidence, RAGRequest, RAGResponse, RAGRetrieval


MAX_EVIDENCE_REACTIONS = 4
MAX_EVIDENCE_COMPOUNDS = 3
MAX_EVIDENCE_PATHWAYS = 2
MAX_EVIDENCE_ENZYMES = 4


def _build_supporting_evidence(retrieved: RAGRetrieval) -> RAGEvidence:
    """Build a bounded evidence subset for answer-panel display.

    The full retrieval payload may be broad for graph exploration. This subset
    is intentionally smaller and answer-oriented.
    """
    focal_compounds: list[RAGCompoundSummary] = []
    resolved_entity_id = retrieved.resolved_entity_id
    if retrieved.interpretation.entity_type == "compound" and resolved_entity_id:
        focal_compounds = [item for item in retrieved.compounds if item.compound_id == resolved_entity_id]
    if not focal_compounds:
        focal_compounds = retrieved.compounds[:MAX_EVIDENCE_COMPOUNDS]

    return RAGEvidence(
        reactions=retrieved.reactions[:MAX_EVIDENCE_REACTIONS],
        compounds=focal_compounds[:MAX_EVIDENCE_COMPOUNDS],
        pathways=retrieved.pathways[:MAX_EVIDENCE_PATHWAYS],
        enzymes=retrieved.enzymes[:MAX_EVIDENCE_ENZYMES],
    )


def run_rag_pipeline(request: RAGRequest) -> RAGResponse:
    """Run the Task 3 RAG pipeline: interpret, retrieve, build context, answer."""
    interpretation = classify_question(request.question)
    retrieved = retrieve_graph_context(interpretation)
    context = build_context(retrieved)
    answer = generate_answer(request.question, context)
    evidence = _build_supporting_evidence(retrieved)
    return RAGResponse(
        answer=answer,
        interpretation=interpretation,
        context=context,
        reactions=retrieved.reactions,
        compounds=retrieved.compounds,
        enzymes=retrieved.enzymes,
        evidence=evidence,
        trace=retrieved.trace,
    )
