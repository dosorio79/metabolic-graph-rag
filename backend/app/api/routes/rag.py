"""RAG query endpoint.

Accepts a natural-language question and returns a graph-grounded answer with
retrieval trace metadata.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.app.rag.pipeline import run_rag_pipeline
from backend.app.schemas.rag import RAGRequest, RAGResponse


router = APIRouter()


@router.post("/query", response_model=RAGResponse)
async def query_rag(request: RAGRequest) -> RAGResponse:
    """Run the RAG pipeline for a single user question."""
    return run_rag_pipeline(request)
