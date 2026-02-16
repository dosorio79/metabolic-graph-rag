"""Pathway retrieval endpoint.
- pathway id, name
- reactions in pathway (id + optional name)
- optionally: summary counts (reactions, compounds, enzymes)

- pathway exists returns 200
- pathway missing returns 404
- payload includes reaction list ordered deterministically (e.g., by id)
"""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.graph import PathwayResponse
from backend.app.services.graph_queries import fetch_pathway

router = APIRouter()

# Pathway retrieval endpoint
@router.get("/{pathway_id}", response_model=PathwayResponse)
async def get_pathway(pathway_id: str) -> PathwayResponse:
    """Retrieve a pathway by its ID."""
    normalized_id = pathway_id.strip()
    payload = fetch_pathway(normalized_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Pathway not found")
    return PathwayResponse(**payload)