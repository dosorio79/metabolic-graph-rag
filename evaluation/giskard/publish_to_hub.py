"""Publish Task 4 dataset/model wrapper artifacts to a Giskard Hub project."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from evaluation.giskard.model_wrapper import rag_predict

DEFAULT_HUB_URL = "http://localhost:19000"
DEFAULT_PROJECT_KEY = "metabolic-graph-rag-task4"
DEFAULT_PROJECT_NAME = "Metabolic Graph RAG Task 4"
DATASET_PATH = Path(__file__).resolve().parent.parent / "dataset" / "questions.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish Task 4 model/dataset to local Giskard Hub")
    parser.add_argument("--hub-url", default=os.getenv("GSK_HUB_URL", DEFAULT_HUB_URL))
    parser.add_argument("--api-key", default=os.getenv("GSK_API_KEY"))
    parser.add_argument("--project-key", default=os.getenv("GSK_PROJECT_KEY", DEFAULT_PROJECT_KEY))
    parser.add_argument("--project-name", default=os.getenv("GSK_PROJECT_NAME", DEFAULT_PROJECT_NAME))
    parser.add_argument("--dataset-path", type=Path, default=DATASET_PATH)
    parser.add_argument(
        "--skip-model-upload",
        action="store_true",
        help="Upload only the dataset (useful if you only want to inspect questions).",
    )
    return parser.parse_args()


def _load_question_records(dataset_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Dataset payload must be a JSON list.")

    rows: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        question = item.get("question")
        if not isinstance(question, str):
            continue
        normalized = question.strip()
        if not normalized:
            continue
        row = dict(item)
        row["question"] = normalized
        rows.append(row)
    return rows


def _prediction_fn(df: Any) -> list[str]:
    questions = df["question"].astype(str).tolist()
    return [rag_predict(question) for question in questions]


def _get_or_create_project(client: Any, project_key: str, project_name: str) -> Any:
    try:
        return client.get_project(project_key)
    except Exception:
        return client.create_project(project_key=project_key, name=project_name, description="Task 4 evaluation assets")


def main() -> int:
    args = _parse_args()
    if not args.api_key:
        raise SystemExit("Missing API key. Set GSK_API_KEY or pass --api-key.")

    import giskard  # type: ignore
    import pandas as pd  # type: ignore

    rows = _load_question_records(args.dataset_path)
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise SystemExit("No non-empty questions found in dataset.")

    client = giskard.GiskardClient(url=args.hub_url, key=args.api_key)
    project = _get_or_create_project(client, args.project_key, args.project_name)

    dataset = giskard.Dataset(
        frame,
        name="task4-questions",
        target=None,
    )
    dataset_id = dataset.upload(client=client, project_key=args.project_key)
    print(f"Uploaded dataset to project '{args.project_key}' (dataset id: {dataset_id})")

    if not args.skip_model_upload:
        model = giskard.Model(
            model=_prediction_fn,
            model_type="text_generation",
            name="metabolic-graph-rag-task4",
            description="Task 4 RAG wrapper for questions.json inspection and scans.",
            feature_names=["question"],
        )
        model_id = model.upload(client=client, project_key=args.project_key)
        print(f"Uploaded model to project '{args.project_key}' (model id: {model_id})")

    print(f"Project ready in Giskard Hub: {args.hub_url} (project key: {args.project_key})")
    print(f"Questions published: {len(frame)}")
    _ = project
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
