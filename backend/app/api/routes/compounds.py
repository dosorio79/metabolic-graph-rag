"""Compound retrieval endpoint skeleton."""

from fastapi import APIRouter

from backend.app.services.name_utils import normalize_name


router = APIRouter()

# Compound retrieval endpoint
@router.get("/{compound_id}")
async def get_compound(compound_id: str):
    """Retrieve a compound by its ID."""
    # Placeholder response - replace with actual retrieval logic
    return {
        "compound_id": compound_id,
        "name": normalize_name("Example Compound"),
        "formula": "C6H12O6",
        "mass": 180.16,
        "reactions": [
            {
                "reaction_id": "R1",
                "name": normalize_name("Reaction 1"),
                "role": "substrate",
            },
            {
                "reaction_id": "R2",
                "name": normalize_name("Reaction 2"),
                "role": "product",
            },
        ],
    }
    