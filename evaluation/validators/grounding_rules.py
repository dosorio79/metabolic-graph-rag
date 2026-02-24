"""Deterministic grounding validators for Task 4 evaluation flows."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

REACTION_ID_RE = re.compile(r"\bR\d{5}\b")
COMPOUND_ID_RE = re.compile(r"\bC\d{5}\b")
EC_NUMBER_RE = re.compile(r"\b(?:\d+|-)\.(?:\d+|-)\.(?:\d+|-)\.(?:\d+|-)\b")

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
    return not (trace.get("retrieved_reactions") or trace.get("retrieved_compounds") or trace.get("retrieved_enzymes"))


def validate_reaction_grounding(trace: dict[str, Any]) -> RuleResult:
    answer_ids = _extract_reaction_ids(trace.get("answer", ""))
    retrieved = set(trace.get("retrieved_reactions", []))
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
    )
    retrieved_entities = set(trace.get("retrieved_reactions", [])) | set(trace.get("retrieved_compounds", [])) | set(
        trace.get("retrieved_enzymes", [])
    )
    overlap = mentioned_entities & retrieved_entities
    return RuleResult(
        rule="retrieval_consistency",
        passed=bool(overlap),
        details=(
            "Answer references at least one retrieved entity."
            if overlap
            else "Answer does not reference any retrieved reaction, compound, or enzyme."
        ),
    )


def validate_insufficient_context_behavior(trace: dict[str, Any]) -> RuleResult:
    if not _retrieval_is_empty(trace):
        return RuleResult(
            rule="insufficient_context_behavior",
            passed=True,
            details="Skipped: retrieval is non-empty.",
        )

    normalized_answer = trace.get("answer", "").lower()
    has_marker = any(marker in normalized_answer for marker in _INSUFFICIENT_CONTEXT_MARKERS)
    return RuleResult(
        rule="insufficient_context_behavior",
        passed=has_marker,
        details=(
            "Answer explicitly states insufficient context."
            if has_marker
            else "Answer should explicitly state insufficient context when retrieval is empty."
        ),
    )


def run_grounding_rules(trace: dict[str, Any]) -> dict[str, Any]:
    """Run all deterministic grounding rules and return pass/fail summary payload."""
    results = [
        validate_reaction_grounding(trace),
        validate_compound_grounding(trace),
        validate_enzyme_grounding(trace),
        validate_retrieval_consistency(trace),
        validate_insufficient_context_behavior(trace),
    ]
    failed_tests = [item.rule for item in results if not item.passed]
    return {
        "grounding_passed": not failed_tests,
        "failed_tests": failed_tests,
        "results": [item.to_dict() for item in results],
    }

