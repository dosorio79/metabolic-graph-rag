"""Pydantic schema definitions for RAG request/response payloads."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RAGReactionSummary(BaseModel):
    reaction_id: str
    name: str | None = None


class RAGCompoundSummary(BaseModel):
    compound_id: str
    name: str | None = None


class RAGInterpretation(BaseModel):
    entity_type: Literal["compound", "reaction", "pathway", "unknown"]
    entity_id: str | None = None
    entity_name: str | None = None
    intent: Literal["producers", "consumers", "participants", "enzymes", "summary", "unknown"]
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RAGTrace(BaseModel):
    reaction_ids: list[str] = Field(default_factory=list)
    compound_ids: list[str] = Field(default_factory=list)
    pathway_ids: list[str] = Field(default_factory=list)
    enzyme_ecs: list[str] = Field(default_factory=list)


class RAGRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("question must not be empty")
        return normalized


class RAGResponse(BaseModel):
    answer: str
    interpretation: RAGInterpretation
    context: str | None = None
    reactions: list[RAGReactionSummary] = Field(default_factory=list)
    compounds: list[RAGCompoundSummary] = Field(default_factory=list)
    enzymes: list[str] = Field(default_factory=list)
    trace: RAGTrace = Field(default_factory=RAGTrace)
