"""Reaction retrieval endpoint.
- reaction id, name, definition, reversible, equation
- substrates: list of {id, name, coef}
- products: list of {id, name, coef}
- enzymes: list of EC numbers

- reaction exists returns 200 with structured payload
- reaction missing returns 404
- coefficients are present and numeric
"""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.graph import ReactionResponse
from backend.app.services.graph_queries import fetch_reaction


router = APIRouter()

# Reaction retrieval endpoint
@router.get("/{reaction_id}", response_model=ReactionResponse)
async def get_reaction(reaction_id: str) -> ReactionResponse:
    """Retrieve a reaction by its ID."""
    normalized_id = reaction_id.strip()
    payload = fetch_reaction(normalized_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Reaction not found")
    return ReactionResponse(**payload)