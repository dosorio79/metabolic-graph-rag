"""Pydantic schema definitions for graph responses."""

from __future__ import annotations

from pydantic import BaseModel


class ReactionSummary(BaseModel):
    reaction_id: str
    name: str | None = None
 
class CompoundAmountSummary(BaseModel):
    compound_id: str
    name: str | None = None
    coef: float


class CompoundResponse(BaseModel):
    compound_id: str
    name: str | None = None
    consuming_reactions: list[ReactionSummary]
    producing_reactions: list[ReactionSummary]

class ReactionResponse(BaseModel):
    reaction_id: str
    name: str | None = None
    equation: str | None = None
    definition: str | None = None
    reversible: bool
    substrates: list[CompoundAmountSummary]
    products: list[CompoundAmountSummary]
    enzymes: list[str]
    
class PathwayReactionsResponse(BaseModel):
    pathway_id: str
    reactions: list[ReactionResponse]


class PathwayResponse(BaseModel):
    pathway_id: str
    name: str | None = None
    reactions: list[ReactionSummary]
    reaction_count: int
    compound_count: int
    enzyme_count: int