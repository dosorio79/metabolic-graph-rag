"""TypedDict definitions for KEGG ingestion outputs."""

from __future__ import annotations

from typing import TypedDict


class CompoundAmount(TypedDict):
    """Compound identifier with stoichiometric coefficient."""

    id: str
    coef: int | float


class ParsedReactionFields(TypedDict):
    """Structured reaction fields parsed from KEGG entries."""

    equation: str | None
    reversible: bool
    substrates: list[CompoundAmount]
    products: list[CompoundAmount]
    enzymes: list[str]
    name: str | None
    definition: str | None


class RawReactionRecord(ParsedReactionFields):
    """Raw reaction fields plus the KEGG reaction identifier."""

    reaction_id: str
    pathway_id: str
    pathway_name: str | None
