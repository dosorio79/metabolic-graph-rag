"""Prefect flow skeleton for ingestion -> enrichment -> loading."""

from __future__ import annotations

from prefect import flow, task

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
        load_reactions(driver, reactions)
    finally:
        driver.close()


@flow(name="kegg_pathway_ingestion")
def ingestion_flow(pathway_id: str = "hsa00010") -> None:
    """Run ingestion -> enrichment -> loading for a single pathway."""
    raw_reactions = ingest_pathway_task(pathway_id)
    enriched_reactions = enrich_entities_task(raw_reactions)
    load_graph_task(enriched_reactions)


if __name__ == "__main__":
    ingestion_flow()
