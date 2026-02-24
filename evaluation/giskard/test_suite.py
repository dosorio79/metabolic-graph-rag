"""Task 4 grounding test suite with optional Giskard orchestration."""

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


def load_questions(dataset_path: Path) -> list[str]:
    """Load evaluation questions from a JSON file."""
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Dataset payload must be a JSON list.")
    questions: list[str] = []
    for item in payload:
        if isinstance(item, dict) and isinstance(item.get("question"), str) and item["question"].strip():
            questions.append(item["question"].strip())
    return questions


def run_grounding_test_cases(questions: list[str]) -> list[dict[str, Any]]:
    """Run deterministic grounding validators for all questions."""
    cases: list[dict[str, Any]] = []
    for question in questions:
        trace = rag_predict_with_trace(question)
        grounded = run_grounding_rules(trace)
        cases.append(
            {
                "question": question,
                "answer": trace["answer"],
                "retrieved_reactions": trace["retrieved_reactions"],
                "retrieved_compounds": trace["retrieved_compounds"],
                "retrieved_enzymes": trace["retrieved_enzymes"],
                "grounding_passed": grounded["grounding_passed"],
                "failed_tests": grounded["failed_tests"],
                "rule_results": grounded["results"],
            }
        )
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
    questions = load_questions(dataset_path)
    cases = run_grounding_test_cases(questions)
    passed = sum(1 for item in cases if item["grounding_passed"])
    failed = len(cases) - passed
    return {
        "total_questions": len(cases),
        "passed_questions": passed,
        "failed_questions": failed,
        "cases": cases,
        "giskard": _run_optional_giskard_scan(questions),
    }
