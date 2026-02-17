"""Rule-based query understanding utilities for Task 3 RAG pipeline."""

from __future__ import annotations

from typing import Any

from backend.app.rag.rules import RULES
from backend.app.rag.utils import normalize_question
from backend.app.schemas.rag import (
    RAGEntityType,
    RAGIntent,
    RAGInterpretation,
)


DebugPayload = dict[str, Any]


def classify_question(question: str) -> RAGInterpretation:
    """Classify a user question into a structured RAG interpretation.

    Args:
        question: Raw user question.
    Returns:
        `RAGInterpretation`.
    """
    result = _classify_question(question, include_debug=False)
    assert isinstance(result, RAGInterpretation)
    return result


def _classify_question(
    question: str, *, include_debug: bool
) -> RAGInterpretation | tuple[RAGInterpretation, DebugPayload]:
    """Internal classifier with optional debug payload emission."""
    normalized = normalize_question(question)
    # Bail out early when text is empty so downstream regex rules do not
    # accidentally classify whitespace/noise as a valid query.
    if not normalized:
        interpretation = RAGInterpretation(entity_type="unknown", intent="unknown", confidence=0.0)
        if not include_debug:
            return interpretation
        return interpretation, _build_debug(
            normalized=normalized,
            intent_before="unknown",
            intent_after="unknown",
            matched_intent_rule=None,
            entity_type_from_id="unknown",
            entity_id=None,
            hinted_type="unknown",
            entity_name=None,
            matched_name_rule=None,
            resolved_entity_type="unknown",
            confidence=0.0,
        )
    # Collect parse signals first, then resolve final intent/entity in one pass.
    intent, matched_intent_rule = _match_intent(normalized, include_rule=include_debug)
    entity_type_from_id, entity_id = _extract_entity_from_ids(normalized)
    hinted_type = _extract_entity_type_hint(normalized)
    entity_name, matched_name_rule = _extract_entity_name(normalized, include_rule=include_debug)

    # Explicit IDs win; fallback rules are only used when no ID-based type was found.
    resolved_entity_type = entity_type_from_id
    if resolved_entity_type == "unknown":
        resolved_entity_type = _fallback_entity_type(intent, hinted_type, entity_name)

    # If the user mentions a known entity without an explicit action word,
    # treat it as a summary request rather than unknown.
    intent_after = intent
    if intent_after == "unknown" and (entity_id or entity_name):
        intent_after = "summary"

    confidence = _score_confidence(
        intent=intent_after,
        entity_type=resolved_entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        hinted_type=hinted_type,
    )
    interpretation = RAGInterpretation(
        entity_type=resolved_entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        intent=intent_after,
        confidence=confidence,
    )
    if not include_debug:
        return interpretation
    # Debug payload mirrors each intermediate decision used to build interpretation.
    return interpretation, _build_debug(
        normalized=normalized,
        intent_before=intent,
        intent_after=intent_after,
        matched_intent_rule=matched_intent_rule,
        entity_type_from_id=entity_type_from_id,
        entity_id=entity_id,
        hinted_type=hinted_type,
        entity_name=entity_name,
        matched_name_rule=matched_name_rule,
        resolved_entity_type=resolved_entity_type,
        confidence=confidence,
    )


def classify_question_with_debug(question: str) -> tuple[RAGInterpretation, DebugPayload]:
    """Return classification plus debug details.

    This wrapper preserves a stable API for callers that explicitly expect the
    debug tuple result.
    """
    result = _classify_question(question, include_debug=True)
    assert isinstance(result, tuple)
    return result


def _match_intent(normalized: str, *, include_rule: bool) -> tuple[RAGIntent, str | None]:
    """Match the first intent by configured priority and optional rule token."""
    for intent in RULES.intent_order:
        for pattern in RULES.intent_patterns[intent]:
            if pattern in normalized:
                return intent, pattern if include_rule else None
    return "unknown", None


def _extract_entity_from_ids(normalized: str) -> tuple[RAGEntityType, str | None]:
    """Extract explicit graph identifiers (compound/reaction/pathway/enzyme)."""
    compound_match = RULES.compound_id_re.search(normalized)
    if compound_match:
        return "compound", compound_match.group(1).upper()

    reaction_match = RULES.reaction_id_re.search(normalized)
    if reaction_match:
        return "reaction", reaction_match.group(1).upper()

    pathway_match = RULES.pathway_id_re.search(normalized)
    if pathway_match:
        return "pathway", pathway_match.group(0).lower()

    enzyme_match = RULES.enzyme_ec_re.search(normalized)
    if enzyme_match and ("ec" in normalized or "enzyme" in normalized):
        return "enzyme", enzyme_match.group(1)
    return "unknown", None


def _extract_entity_type_hint(normalized: str) -> RAGEntityType:
    """Infer entity type from lexical hints when no explicit ID is present."""
    for entity_type in RULES.entity_type_order:
        if any(hint in normalized for hint in RULES.entity_type_hints[entity_type]):
            return entity_type
    return "unknown"


def _extract_entity_name(normalized: str, *, include_rule: bool) -> tuple[str | None, str | None]:
    """Extract candidate entity name from phrase patterns and sanitize it."""
    for pattern in RULES.name_patterns:
        match = pattern.search(normalized)
        if not match:
            continue
        tokens = [token for token in match.group("name").split() if token not in RULES.stopwords]
        name = " ".join(tokens).strip(" ?.,;:")
        if name:
            return name, pattern.pattern if include_rule else None
    return None, None


def _fallback_entity_type(
    intent: RAGIntent, hinted_type: RAGEntityType, entity_name: str | None
) -> RAGEntityType:
    """Resolve ambiguous entity type using intent-aware heuristics."""
    if intent == "participants" and hinted_type == "enzyme" and entity_name is None:
        return "enzyme"
    if intent == "participants" and hinted_type == "enzyme" and entity_name is not None:
        return "compound"
    if intent == "participants":
        return "reaction"
    if intent in {"producers", "consumers"} and entity_name:
        return "compound"
    if hinted_type != "unknown":
        return hinted_type
    return "unknown"


def _score_confidence(
    intent: RAGIntent,
    entity_type: RAGEntityType,
    entity_id: str | None,
    entity_name: str | None,
    hinted_type: RAGEntityType,
) -> float:
    """Compute bounded confidence score from matched classification signals."""
    if intent == "unknown" and not entity_id and not entity_name:
        return 0.0

    score = 0.2
    if intent != "unknown":
        score += 0.3
    if entity_id:
        score += 0.35
    if entity_name:
        score += 0.2
    if entity_type != "unknown":
        score += 0.1
    if hinted_type != "unknown" and hinted_type != entity_type:
        score -= 0.15
    return max(0.0, min(score, 0.99))


def _build_debug(
    *,
    normalized: str,
    intent_before: RAGIntent,
    intent_after: RAGIntent,
    matched_intent_rule: str | None,
    entity_type_from_id: RAGEntityType,
    entity_id: str | None,
    hinted_type: RAGEntityType,
    entity_name: str | None,
    matched_name_rule: str | None,
    resolved_entity_type: RAGEntityType,
    confidence: float,
) -> dict[str, Any]:
    """Build a stable debug payload for parser inspection and logging."""
    return {
        "normalized_question": normalized,
        "intent_before_promotion": intent_before,
        "intent_after_promotion": intent_after,
        "matched_intent_rule": matched_intent_rule,
        "entity_type_from_id": entity_type_from_id,
        "entity_id_from_id": entity_id,
        "hinted_entity_type": hinted_type,
        "extracted_entity_name": entity_name,
        "matched_name_rule": matched_name_rule,
        "resolved_entity_type": resolved_entity_type,
        "fallback_applied": entity_type_from_id == "unknown" and resolved_entity_type != "unknown",
        "confidence": confidence,
    }
