"""Manual test script for loading KEGG reactions into Neo4j."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from etl.config import get_settings
from etl.load.neo4j_loader import get_driver, load_reactions
from etl.normalize.kegg_pipeline import ingest_pathway


def _parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Load KEGG reactions into Neo4j")
    parser.add_argument("pathway_id", nargs="?", default="hsa00010")
    parser.add_argument(
        "--uri",
        default=settings.neo4j_uri,
    )
    parser.add_argument(
        "--user",
        default=settings.neo4j_user,
    )
    parser.add_argument(
        "--password",
        default=settings.neo4j_password,
    )
    return parser.parse_args()


def main() -> None:
    """Fetch reactions for a pathway and load them into Neo4j."""
    args = _parse_args()
    driver = get_driver(uri=args.uri, user=args.user, password=args.password)
    try:
        reactions = ingest_pathway(args.pathway_id)
        load_reactions(driver, reactions)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
