"""CLI entrypoint to run Task 4 answer-grounding evaluation."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.giskard.test_suite import run_test_suite

DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset" / "questions.json"
RESULTS_PATH = Path(__file__).resolve().parent.parent / "results" / "latest_results.json"


def main() -> int:
    report = run_test_suite(DATASET_PATH)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Questions: {report['total_questions']}")
    print(f"Passed: {report['passed_questions']}")
    print(f"Failed: {report['failed_questions']}")
    giskard_report = report.get("giskard", {})
    print(f"Giskard status: {giskard_report.get('status', 'unknown')}")
    if giskard_report.get("reason"):
        print(f"Giskard note: {giskard_report['reason']}")
    print(f"Results written to: {RESULTS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

