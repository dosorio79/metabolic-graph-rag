"""Deterministic grounding validators for Task 4 evaluation flows."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

REACTION_ID_RE = re.compile(r"\bR\d{5}\b")
COMPOUND_ID_RE = re.compile(r"\bC\d{5}\b")
EC_NUMBER_RE = re.compile(r"\b(?:\d+|-)\.(?:\d+|-)\.(?:\d+|-)\.(?:\d+|-)\b")
_PATHWAY_CONTEXT_LINE_RE = re.compile(r"^- ([A-Za-z0-9]+) \((.+)\)$")

_INSUFFICIENT_CONTEXT_MARKERS = (
    "insufficient context",
    "not enough context",
    "insufficient information",
    "not enough information",
    "cannot answer from the retrieved context",
    "unable to answer from the retrieved context",
)


@dataclass(frozen=True)
class RuleResult:
    """Normalized pass/fail payload for a single grounding rule."""

    rule: str
    passed: bool
    details: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_reaction_ids(answer: str) -> set[str]:
    return set(REACTION_ID_RE.findall(answer))


def _extract_compound_ids(answer: str) -> set[str]:
    return set(COMPOUND_ID_RE.findall(answer))


def _extract_ec_numbers(answer: str) -> set[str]:
    return set(EC_NUMBER_RE.findall(answer))


def _retrieval_is_empty(trace: dict[str, Any]) -> bool:
    if "retrieval_empty" in trace:
        return bool(trace["retrieval_empty"])
    return not (trace.get("retrieved_reactions") or trace.get("retrieved_compounds") or trace.get("retrieved_enzymes"))


def _answer_has_insufficient_context_marker(answer: str) -> bool:
    normalized_answer = answer.lower()
    return any(marker in normalized_answer for marker in _INSUFFICIENT_CONTEXT_MARKERS)


def _extract_pathway_names_from_context(context: str) -> set[str]:
    """Extract normalized pathway names from the rendered context section."""
    pathway_names: set[str] = set()
    in_pathways_section = False
    for raw_line in context.splitlines():
        line = raw_line.strip()
        if line == "Pathways:":
            in_pathways_section = True
            continue
        if in_pathways_section and (not line or not line.startswith("- ")):
            in_pathways_section = False
            continue
        if not in_pathways_section:
            continue
        match = _PATHWAY_CONTEXT_LINE_RE.match(line)
        if not match:
            continue
        pathway_name = match.group(2).strip().lower()
        if pathway_name:
            pathway_names.add(pathway_name)
    return pathway_names


def validate_reaction_grounding(trace: dict[str, Any]) -> RuleResult:
    answer_ids = _extract_reaction_ids(trace.get("answer", ""))
    retrieved = set(trace.get("retrieved_reactions", []))
    focal_reaction_id = trace.get("interpretation", {}).get("entity_id")
    if _retrieval_is_empty(trace) and isinstance(focal_reaction_id, str) and focal_reaction_id:
        # When retrieval is empty, the model may legitimately restate the asked
        # reaction identifier while explaining that details were not found.
        retrieved.add(focal_reaction_id)
    extras = sorted(answer_ids - retrieved)
    return RuleResult(
        rule="reaction_grounding",
        passed=not extras,
        details="All reaction IDs are grounded." if not extras else f"Ungrounded reaction IDs: {', '.join(extras)}",
    )


def validate_compound_grounding(trace: dict[str, Any]) -> RuleResult:
    answer_ids = _extract_compound_ids(trace.get("answer", ""))
    retrieved = set(trace.get("retrieved_compounds", []))
    extras = sorted(answer_ids - retrieved)
    return RuleResult(
        rule="compound_grounding",
        passed=not extras,
        details="All compound IDs are grounded." if not extras else f"Ungrounded compound IDs: {', '.join(extras)}",
    )


def validate_enzyme_grounding(trace: dict[str, Any]) -> RuleResult:
    answer_ids = _extract_ec_numbers(trace.get("answer", ""))
    retrieved = set(trace.get("retrieved_enzymes", []))
    extras = sorted(answer_ids - retrieved)
    return RuleResult(
        rule="enzyme_grounding",
        passed=not extras,
        details="All enzyme EC numbers are grounded." if not extras else f"Ungrounded enzyme EC numbers: {', '.join(extras)}",
    )


def validate_retrieval_consistency(trace: dict[str, Any]) -> RuleResult:
    if _retrieval_is_empty(trace):
        return RuleResult(
            rule="retrieval_consistency",
            passed=True,
            details="Skipped: retrieval is empty.",
        )

    answer = trace.get("answer", "")
    mentioned_entities = (
        _extract_reaction_ids(answer)
        | _extract_compound_ids(answer)
        | _extract_ec_numbers(answer)
        | set(pathway_id for pathway_id in trace.get("trace_pathway_ids", []) if pathway_id in answer)
    )
    retrieved_entities = set(trace.get("retrieved_reactions", [])) | set(trace.get("retrieved_compounds", [])) | set(
        trace.get("retrieved_enzymes", [])
    ) | set(trace.get("trace_pathway_ids", []))
    overlap = mentioned_entities & retrieved_entities
    return RuleResult(
        rule="retrieval_consistency",
        passed=bool(overlap),
        details=(
            "Answer references at least one retrieved entity."
            if overlap
            else "Answer does not reference any retrieved reaction, compound, enzyme, or pathway."
        ),
    )


def validate_insufficient_context_behavior(trace: dict[str, Any]) -> RuleResult:
    if not _retrieval_is_empty(trace):
        return RuleResult(
            rule="insufficient_context_behavior",
            passed=True,
            details="Skipped: retrieval is non-empty.",
        )

    has_marker = _answer_has_insufficient_context_marker(trace.get("answer", ""))
    return RuleResult(
        rule="insufficient_context_behavior",
        passed=has_marker,
        details=(
            "Answer explicitly states insufficient context."
            if has_marker
            else "Answer should explicitly state insufficient context when retrieval is empty."
        ),
    )


def validate_expected_intent(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    expected_intent = expectations.get("expected_intent")
    if not expected_intent:
        return RuleResult(rule="expected_intent", passed=True, details="Skipped: no expected intent.")
    actual_intent = trace.get("interpretation", {}).get("intent")
    return RuleResult(
        rule="expected_intent",
        passed=actual_intent == expected_intent,
        details=(
            f"Interpretation intent matches expected value `{expected_intent}`."
            if actual_intent == expected_intent
            else f"Expected intent `{expected_intent}`, got `{actual_intent}`."
        ),
    )


def validate_expected_entity_type(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    expected_entity_type = expectations.get("expected_entity_type")
    if not expected_entity_type:
        return RuleResult(rule="expected_entity_type", passed=True, details="Skipped: no expected entity type.")
    actual_entity_type = trace.get("interpretation", {}).get("entity_type")
    return RuleResult(
        rule="expected_entity_type",
        passed=actual_entity_type == expected_entity_type,
        details=(
            f"Interpretation entity type matches expected value `{expected_entity_type}`."
            if actual_entity_type == expected_entity_type
            else f"Expected entity type `{expected_entity_type}`, got `{actual_entity_type}`."
        ),
    )


def validate_non_empty_retrieval(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    if not expectations.get("expect_non_empty_retrieval"):
        return RuleResult(rule="non_empty_retrieval", passed=True, details="Skipped: non-empty retrieval not required.")
    empty = _retrieval_is_empty(trace)
    return RuleResult(
        rule="non_empty_retrieval",
        passed=not empty,
        details="Retrieval is non-empty." if not empty else "Expected non-empty retrieval, but retrieval was empty.",
    )


def validate_no_false_insufficient_context(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    if not expectations.get("expect_no_insufficient_context"):
        return RuleResult(
            rule="no_false_insufficient_context",
            passed=True,
            details="Skipped: insufficient-context prohibition not required.",
        )
    answer = trace.get("answer", "")
    has_marker = _answer_has_insufficient_context_marker(answer)
    return RuleResult(
        rule="no_false_insufficient_context",
        passed=not has_marker,
        details=(
            "Answer does not claim insufficient context."
            if not has_marker
            else "Answer claims insufficient context despite expectation for a substantive answer."
        ),
    )


def validate_reaction_citation_expectation(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    if not expectations.get("expect_reaction_citation"):
        return RuleResult(
            rule="reaction_citation_expectation",
            passed=True,
            details="Skipped: reaction citation not required.",
        )
    answer_ids = _extract_reaction_ids(trace.get("answer", ""))
    return RuleResult(
        rule="reaction_citation_expectation",
        passed=bool(answer_ids),
        details=(
            "Answer cites at least one reaction ID."
            if answer_ids
            else "Expected the answer to cite at least one reaction ID."
        ),
    )


def validate_pathway_reference_in_answer(trace: dict[str, Any], expectations: dict[str, Any]) -> RuleResult:
    if not expectations.get("expect_pathway_reference_in_answer"):
        return RuleResult(
            rule="pathway_reference_in_answer",
            passed=True,
            details="Skipped: pathway reference not required.",
        )
    answer = trace.get("answer", "")
    normalized_answer = answer.lower()
    pathway_ids = [pathway_id for pathway_id in trace.get("trace_pathway_ids", []) if pathway_id]
    matched_ids = [pathway_id for pathway_id in pathway_ids if pathway_id in answer]
    context_pathway_names = _extract_pathway_names_from_context(trace.get("context", ""))
    matched_names = [name for name in sorted(context_pathway_names) if name in normalized_answer]
    interpreted_entity_name = trace.get("interpretation", {}).get("entity_name")
    matched_interpreted_name: list[str] = []
    if (
        trace.get("interpretation", {}).get("entity_type") == "pathway"
        and isinstance(interpreted_entity_name, str)
        and interpreted_entity_name
        and interpreted_entity_name.lower() in normalized_answer
    ):
        matched_interpreted_name = [interpreted_entity_name.lower()]
    matched_references = matched_ids + matched_names + matched_interpreted_name
    return RuleResult(
        rule="pathway_reference_in_answer",
        passed=bool(matched_references),
        details=(
            f"Answer references grounded pathway marker(s): {', '.join(matched_references)}."
            if matched_references
            else "Expected the answer to reference at least one retrieved pathway ID or pathway name from context."
        ),
    )


def run_grounding_rules(trace: dict[str, Any], expectations: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run all deterministic grounding rules and return pass/fail summary payload."""
    expectations = expectations or {}
    results = [
        validate_reaction_grounding(trace),
        validate_compound_grounding(trace),
        validate_enzyme_grounding(trace),
        validate_retrieval_consistency(trace),
        validate_insufficient_context_behavior(trace),
        validate_expected_intent(trace, expectations),
        validate_expected_entity_type(trace, expectations),
        validate_non_empty_retrieval(trace, expectations),
        validate_no_false_insufficient_context(trace, expectations),
        validate_reaction_citation_expectation(trace, expectations),
        validate_pathway_reference_in_answer(trace, expectations),
    ]
    failed_tests = [item.rule for item in results if not item.passed]
    return {
        "grounding_passed": not failed_tests,
        "failed_tests": failed_tests,
        "results": [item.to_dict() for item in results],
    }
