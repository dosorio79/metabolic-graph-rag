"""Orchestrate KEGG ingestion for manual runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from etl.normalize.kegg_pipeline import ingest_pathway


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the KEGG ingestion run.

    Returns:
        Parsed command-line arguments.
    """
    # Configure CLI flags for pathway selection and output.
    parser = argparse.ArgumentParser(description="Run KEGG ingestion pipeline")
    parser.add_argument(
        "pathway_id",
        nargs="?",
        default="hsa00010",
        help="KEGG pathway id (default: hsa00010)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output JSON path",
    )
    return parser.parse_args()


def main() -> int:
    """Run the ingestion pipeline and optionally write results to JSON.

    Returns:
        Exit status code.
    """
    # Run ingestion with the requested pathway id.
    args = _parse_args()

    reactions = ingest_pathway(args.pathway_id)

    # Persist results when an output path is provided.
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(reactions, indent=2), encoding="utf-8")
        print(f"Wrote {len(reactions)} reactions to {args.output}")
        return 0

    if reactions:
        print("\nExample reaction:")
        print(reactions[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
