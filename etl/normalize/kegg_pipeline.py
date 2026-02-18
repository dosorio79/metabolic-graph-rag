"""KEGG ingestion pipeline utilities."""

from __future__ import annotations

import requests

from etl.fetch.kegg_api import fetch_kegg_data
from etl.normalize.kegg_modules import extract_kegg_modules
from etl.models.kegg_types import RawReactionRecord
from etl.normalize.kegg_reactions import extract_kegg_reactions, parse_reaction_entry
from etl.normalize.name_utils import normalize_name


def ingest_pathway(pathway_id: str) -> list[RawReactionRecord]:
    """Ingest a pathway into raw reaction topology records.

    Pipeline:
        Pathway -> Modules -> Reactions -> Parsed reactions

    Args:
        pathway_id: KEGG pathway id (e.g., "hsa00010").

    Returns:
        Raw reaction records for the pathway.
    """

    # Create a shared session for all KEGG requests.
    session = requests.Session()

    # Fetch pathway entry and extract module ids.
    print(f"\nFetching pathway: {pathway_id}")
    pathway_text = fetch_kegg_data("get", pathway_id, session=session)

    pathway_name = _extract_pathway_name(pathway_text)
    modules = extract_kegg_modules(pathway_text)
    print(f"Modules discovered: {len(modules)}")

    # Fetch each module entry and collect reaction ids.
    all_reactions: set[str] = set()

    for module in modules:
        module_text = fetch_kegg_data("get", module, session=session)
        reactions = extract_kegg_reactions(module_text)
        all_reactions.update(reactions)

    # Module sections can be incomplete for organism-specific pathways.
    # Always union direct pathway reaction references to maximize coverage.
    all_reactions.update(extract_kegg_reactions(pathway_text))
    # KEGG pathway entries often omit explicit R-ids; the pathway->reaction
    # link endpoint is a more reliable source of reaction membership.
    pathway_links_text = fetch_kegg_data("link/rn", pathway_id, session=session)
    all_reactions.update(extract_kegg_reactions(pathway_links_text))

    print(f"Total reactions collected: {len(all_reactions)}")

    # Fetch each reaction entry and parse into structured records.
    parsed_reactions: list[RawReactionRecord] = []
    skipped_reactions: list[str] = []

    for reaction_id in sorted(all_reactions):
        reaction_text = fetch_kegg_data("get", reaction_id, session=session)

        parsed = parse_reaction_entry(reaction_text)

        if not parsed["equation"] or not parsed["substrates"] or not parsed["products"]:
            skipped_reactions.append(reaction_id)
            continue

        parsed_record: RawReactionRecord = {
            "reaction_id": reaction_id,
            "pathway_id": pathway_id,
            "pathway_name": pathway_name,
            **parsed,
        }
        parsed_reactions.append(parsed_record)

    missing_count = len(skipped_reactions)
    print(f"Missing reactions: {missing_count}")
    if skipped_reactions:
        print(f"Skipped: {', '.join(sorted(skipped_reactions))}")
    print(f"Parsed reactions: {len(parsed_reactions)}")

    return parsed_reactions


def _extract_pathway_name(text: str) -> str | None:
    """Extract the pathway NAME field from a KEGG pathway entry."""
    name = ""
    capture = False

    for line in text.splitlines():
        if line.startswith("NAME"):
            capture = True
            name = line.replace("NAME", "", 1).strip()
            continue

        if capture:
            if line.startswith(" "):
                name += " " + line.strip()
            else:
                break

    return normalize_name(name)
