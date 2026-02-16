"""Compound retrieval endpoint
Returns:
- compound id, name
- reactions that CONSUME it
- reactions that PRODUCE it

- compound exists returns 200 with structured payload
- compound missing returns 404 with clear message
- payload includes both consuming and producing reaction lists

"""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.graph import CompoundResponse
from backend.app.services.graph_queries import fetch_compound


router = APIRouter()

# Compound retrieval endpoint
@router.get("/{compound_id}", response_model=CompoundResponse)
async def get_compound(compound_id: str) -> CompoundResponse:
    """Retrieve a compound by its ID."""
    normalized_id = compound_id.strip()
    payload = fetch_compound(normalized_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Compound not found")
    return CompoundResponse(**payload)

