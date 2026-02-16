"""Reaction retrieval endpoint skeleton."""

from fastapi import APIRouter

from backend.app.services.name_utils import normalize_name


router = APIRouter()

# Reaction retrieval endpoint
@router.get("/{reaction_id}")
async def get_reaction(reaction_id: str):
    """Retrieve a reaction by its ID."""
    # Placeholder response - replace with actual retrieval logic
    return {
        "reaction_id": reaction_id,
        "name": normalize_name("Example Reaction"),
        "definition": "This is a placeholder reaction. Replace with actual data.",
        "reversible": True,
        "pathway": {"pathway_id": "P1", "name": normalize_name("Example Pathway")},
        "compounds": [
            {
                "compound_id": "C1",
                "name": normalize_name("Compound 1"),
                "role": "substrate",
            },
            {
                "compound_id": "C2",
                "name": normalize_name("Compound 2"),
                "role": "product",
            },
        ],
    }