"""Prefect flow skeleton for ingestion -> enrichment -> loading."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from prefect import flow, task

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from etl.enrich.compound_enrichment import enrich_compound_names
from etl.load.neo4j_loader import get_driver, load_reactions
from etl.models.kegg_types import RawReactionRecord
from etl.normalize.kegg_pipeline import ingest_pathway


@task
def ingest_pathway_task(pathway_id: str) -> list[RawReactionRecord]:
    """Ingest raw reactions for a pathway."""
    return ingest_pathway(pathway_id)


@task
def enrich_entities_task(reactions: list[RawReactionRecord]) -> list[RawReactionRecord]:
    """Enrich reactions with compound metadata."""
    return enrich_compound_names(reactions)


@task
def load_graph_task(reactions: list[RawReactionRecord]) -> None:
    """Load enriched reactions into Neo4j."""
    driver = get_driver()
    try:
        _apply_schema(driver)
        load_reactions(driver, reactions)
    finally:
        driver.close()


@task(persist_result=True)
def ingest_stats(reactions: list[RawReactionRecord]) -> dict[str, int]:
    """Persist basic ingestion stats for observability."""
    compound_ids: set[str] = set()
    for reaction in reactions:
        for compound in reaction.get("substrates", []):
            compound_ids.add(compound["id"])
        for compound in reaction.get("products", []):
            compound_ids.add(compound["id"])

    return {
        "reactions": len(reactions),
        "compounds": len(compound_ids),
    }


@flow(name="kegg_pathway_ingestion")
def ingestion_flow(pathway_id: str = "hsa00010") -> None:
    """Run ingestion -> enrichment -> loading for a single pathway."""
    raw_reactions = ingest_pathway_task(pathway_id)
    enriched_reactions = enrich_entities_task(raw_reactions)
    ingest_stats(enriched_reactions)
    load_graph_task(enriched_reactions)


@flow(name="kegg_batch_pathway_ingestion")
def batch_ingestion_flow(
    pathway_ids: list[str] | str,
    continue_on_error: bool = True,
) -> dict[str, object]:
    """Run ingestion for multiple pathways and return per-pathway outcomes."""
    normalized_ids = _normalize_pathway_ids(pathway_ids)
    successes: list[str] = []
    failures: list[dict[str, str]] = []

    for pathway_id in normalized_ids:
        try:
            raw_reactions = ingest_pathway_task(pathway_id)
            enriched_reactions = enrich_entities_task(raw_reactions)
            ingest_stats(enriched_reactions)
            load_graph_task(enriched_reactions)
            successes.append(pathway_id)
        except Exception as exc:  # pragma: no cover - orchestration boundary
            failures.append({"pathway_id": pathway_id, "error": str(exc)})
            if not continue_on_error:
                raise

    return {
        "total": len(normalized_ids),
        "success_count": len(successes),
        "failure_count": len(failures),
        "successes": successes,
        "failures": failures,
    }


def _apply_schema(driver) -> None:
    """Apply graph schema constraints before ingestion."""
    schema_path = REPO_ROOT / "graph" / "schema.cypher"
    if not schema_path.exists():
        return

    statements = [
        stmt.strip()
        for stmt in schema_path.read_text().split(";")
        if stmt.strip()
    ]

    with driver.session() as session:
        for statement in statements:
            session.run(statement)


def _parse_args() -> argparse.Namespace:
    """Parse local CLI arguments for single or batch ingestion runs."""
    parser = argparse.ArgumentParser(description="Run Prefect KEGG ingestion flows")
    parser.add_argument(
        "--pathway-id",
        default="hsa00010",
        help="Single KEGG pathway id (default: hsa00010)",
    )
    parser.add_argument(
        "--pathway-ids",
        nargs="+",
        help="One or more KEGG pathway ids for batch ingestion",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop batch ingestion at first failure",
    )
    return parser.parse_args()


def _normalize_pathway_ids(pathway_ids: list[str] | str) -> list[str]:
    """Normalize UI/CLI pathway inputs into a clean list of ids.

    Prefect UI can pass list params either as a JSON list or as a single string.
    Accept both and split on commas/whitespace when needed.
    """
    if isinstance(pathway_ids, str):
        raw = pathway_ids.strip()
        if not raw:
            return []
        # Prefer strict JSON parsing when UI sends a JSON array string.
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = None
            if isinstance(parsed, list):
                return _normalize_pathway_ids(parsed)
        tokens = raw.replace(",", " ").split()
        cleaned = [token.strip("[]\"' ") for token in tokens if token.strip("[]\"' ")]
        return cleaned
    normalized: list[str] = []
    for item in pathway_ids:
        if not item:
            continue
        # Some UIs send a list with one CSV/JSON-like string item; split it too.
        normalized.extend(_normalize_pathway_ids(item))
    # Keep order while removing duplicates.
    deduped: list[str] = []
    seen: set[str] = set()
    for item in normalized:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


if __name__ == "__main__":
    args = _parse_args()
    if args.pathway_ids:
        batch_ingestion_flow(
            pathway_ids=args.pathway_ids,
            continue_on_error=not args.fail_fast,
        )
    else:
        ingestion_flow(pathway_id=args.pathway_id)
