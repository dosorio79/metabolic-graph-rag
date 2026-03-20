"""Task 4/6 grounding test suite with optional Giskard orchestration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from evaluation.giskard.model_wrapper import rag_predict, rag_predict_with_trace
from evaluation.validators.grounding_rules import run_grounding_rules

_GISKARD_IMPORT_ERROR: str | None = None

try:  # pragma: no cover - optional dependency path
    import giskard  # type: ignore
    import pandas as pd  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency path
    giskard = None
    pd = None
    _GISKARD_IMPORT_ERROR = f"{exc.__class__.__name__}: {exc}"


def _scan_enabled() -> bool:
    return os.getenv("APP_TASK4_ENABLE_GISKARD_SCAN", "").strip().lower() in {"1", "true", "yes", "on"}


def load_cases(dataset_path: Path) -> list[dict[str, Any]]:
    """Load evaluation cases from a JSON file.

    The dataset is intentionally permissive:
    - existing Task 4 entries that only define `question` remain valid
    - Task 6 entries may include richer expectation metadata consumed later
    """
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Dataset payload must be a JSON list.")
    cases: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        question = item.get("question")
        if not isinstance(question, str) or not question.strip():
            continue
        case = dict(item)
        case["question"] = question.strip()
        cases.append(case)
    return cases


def load_questions(dataset_path: Path) -> list[str]:
    """Return question text only for callers that only need the raw prompts."""
    return [case["question"] for case in load_cases(dataset_path)]


def run_grounding_test_cases(dataset_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run deterministic grounding validators for all evaluation cases."""
    cases: list[dict[str, Any]] = []
    for case in dataset_cases:
        question = case["question"]
        trace = rag_predict_with_trace(question)
        expectations = {key: value for key, value in case.items() if key not in {"question", "source", "category"}}
        grounded = run_grounding_rules(trace, expectations=expectations)
        cases.append(
            {
                "category": case.get("category"),
                "question": question,
                "source": case.get("source"),
                "expectations": expectations,
                "answer": trace["answer"],
                "prompt_versions": trace.get("prompt_versions", {}),
                "system_prompt_version": trace.get("system_prompt_version"),
                "user_prompt_version": trace.get("user_prompt_version"),
                "interpretation": trace.get("interpretation", {}),
                "retrieved_reactions": trace["retrieved_reactions"],
                "retrieved_compounds": trace["retrieved_compounds"],
                "retrieved_enzymes": trace["retrieved_enzymes"],
                "trace_pathway_ids": trace.get("trace_pathway_ids", []),
                "retrieval_empty": trace.get("retrieval_empty", False),
                "grounding_passed": grounded["grounding_passed"],
                "failed_tests": grounded["failed_tests"],
                "rule_results": grounded["results"],
            }
        )
    return cases


def _append_case_rule(case: dict[str, Any], *, rule: str, passed: bool, details: str) -> None:
    """Append a synthetic case-level rule result and update aggregate status."""
    case["rule_results"].append({"rule": rule, "passed": passed, "details": details})
    if not passed and rule not in case["failed_tests"]:
        case["failed_tests"].append(rule)
        case["grounding_passed"] = False


def apply_pairwise_expectation_rules(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply cross-case regression checks such as name-vs-ID parity."""
    by_question = {case["question"]: case for case in cases}
    for case in cases:
        expectations = case.get("expectations", {})

        equivalent_question = expectations.get("resolution_equivalent_to")
        if equivalent_question:
            peer = by_question.get(equivalent_question)
            if peer is None:
                _append_case_rule(
                    case,
                    rule="resolution_equivalence",
                    passed=True,
                    details=f"Skipped: paired case `{equivalent_question}` not present in this run.",
                )
            else:
                same_empty_state = bool(case.get("retrieval_empty")) == bool(peer.get("retrieval_empty"))
                shared_compounds = sorted(set(case.get("retrieved_compounds", [])) & set(peer.get("retrieved_compounds", [])))
                passed = same_empty_state and bool(shared_compounds)
                if passed:
                    details = f"Resolution parity holds with `{equivalent_question}` via compounds: {', '.join(shared_compounds)}."
                elif case.get("retrieval_empty") != peer.get("retrieval_empty"):
                    details = (
                        f"Resolution parity failed with `{equivalent_question}`: one query resolved graph context and the other did not."
                    )
                else:
                    details = (
                        f"Resolution parity failed with `{equivalent_question}`: no shared retrieved compounds were found."
                    )
                _append_case_rule(case, rule="resolution_equivalence", passed=passed, details=details)
    return cases


def _run_optional_giskard_scan(questions: list[str]) -> dict[str, Any]:
    """Run a lightweight Giskard scan when dependency is available."""
    if giskard is None or pd is None:
        return {
            "available": False,
            "status": "skipped",
            "reason": "giskard import unavailable" if _GISKARD_IMPORT_ERROR else "giskard is not installed",
            "import_error": _GISKARD_IMPORT_ERROR,
        }

    if not _scan_enabled():
        return {
            "available": True,
            "status": "skipped",
            "reason": "set APP_TASK4_ENABLE_GISKARD_SCAN=1 to enable optional giskard.scan (may incur LLM API cost)",
        }

    frame = pd.DataFrame({"question": questions})

    def prediction_fn(df: Any) -> list[str]:
        return [rag_predict(question) for question in df["question"].astype(str).tolist()]

    model = giskard.Model(
        model=prediction_fn,
        model_type="text_generation",
        name="metabolic-graph-rag",
        description="Task 4 RAG wrapper for grounding evaluation.",
        feature_names=["question"],
    )
    dataset = giskard.Dataset(
        frame,
        name="task4-grounding-questions",
        target=None,
    )
    scan = giskard.scan(model=model, dataset=dataset)
    return {
        "available": True,
        "status": "completed",
        "scan_has_issues": bool(getattr(scan, "issues", [])),
        "issue_count": len(getattr(scan, "issues", [])),
    }


def run_test_suite(dataset_path: Path) -> dict[str, Any]:
    """Execute deterministic grounding tests and optional Giskard scan."""
    dataset_cases = load_cases(dataset_path)
    questions = [case["question"] for case in dataset_cases]
    cases = apply_pairwise_expectation_rules(run_grounding_test_cases(dataset_cases))
    passed = sum(1 for item in cases if item["grounding_passed"])
    failed = len(cases) - passed
    return {
        "total_questions": len(cases),
        "passed_questions": passed,
        "failed_questions": failed,
        "cases": cases,
        "giskard": _run_optional_giskard_scan(questions),
    }
