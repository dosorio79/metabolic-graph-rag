"""Pydantic schema definitions for RAG request/response payloads."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RAGEntityType = Literal["compound", "reaction", "pathway", "enzyme", "unknown"]
RAGIntent = Literal["producers", "consumers", "participants", "summary", "unknown"]


@dataclass(frozen=True)
class QueryRules:
    intent_order: tuple[RAGIntent, ...]
    entity_type_order: tuple[RAGEntityType, ...]
    intent_patterns: dict[RAGIntent, tuple[str, ...]]
    entity_type_hints: dict[RAGEntityType, tuple[str, ...]]
    name_patterns: tuple[re.Pattern[str], ...]
    stopwords: set[str]
    compound_id_re: re.Pattern[str]
    reaction_id_re: re.Pattern[str]
    pathway_id_re: re.Pattern[str]
    enzyme_ec_re: re.Pattern[str]


class RAGReactionSummary(BaseModel):
    reaction_id: str
    name: str | None = None


class RAGCompoundSummary(BaseModel):
    compound_id: str
    name: str | None = None


class RAGInterpretation(BaseModel):
    entity_type: RAGEntityType
    entity_id: str | None = None
    entity_name: str | None = None
    intent: RAGIntent
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class RAGTrace(BaseModel):
    reaction_ids: list[str] = Field(default_factory=list)
    compound_ids: list[str] = Field(default_factory=list)
    pathway_ids: list[str] = Field(default_factory=list)
    enzyme_ecs: list[str] = Field(default_factory=list)


class RAGRetrieval(BaseModel):
    interpretation: RAGInterpretation
    resolved_entity_id: str | None = None
    reactions: list[RAGReactionSummary] = Field(default_factory=list)
    compounds: list[RAGCompoundSummary] = Field(default_factory=list)
    enzymes: list[str] = Field(default_factory=list)
    trace: RAGTrace = Field(default_factory=RAGTrace)


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
