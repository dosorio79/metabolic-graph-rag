"""Pathway retrieval endpoint skeleton."""

from fastapi import APIRouter

from backend.app.services.name_utils import normalize_name


router = APIRouter()

# Pathway retrieval endpoint
@router.get("/{pathway_id}")
async def get_pathway(pathway_id: str):
    """Retrieve a pathway by its ID."""
    # Placeholder response - replace with actual retrieval logic
    return {
        "pathway_id": pathway_id,
        "name": normalize_name("Example Pathway"),
        "description": "This is a placeholder pathway. Replace with actual data.",
        "reactions": [
            {"reaction_id": "R1", "name": normalize_name("Reaction 1")},
            {"reaction_id": "R2", "name": normalize_name("Reaction 2")},
        ],
    }