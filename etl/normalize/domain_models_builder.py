"""Build typed domain models from raw ingestion records."""

from __future__ import annotations

from etl.models.domain_models import Compound, Enzyme, ParsedReaction, Reaction
from etl.models.kegg_types import RawReactionRecord


def build_parsed_reactions(raw_reactions: list[RawReactionRecord]) -> list[ParsedReaction]:
    """Convert raw reaction dicts into typed model instances.

    Args:
        raw_reactions: Raw records from the ingestion pipeline.

    Returns:
        Typed ParsedReaction entries suitable for downstream loaders.
    """
    parsed_reactions: list[ParsedReaction] = []

    for raw in raw_reactions:
        reaction_id = raw["reaction_id"]
        equation = raw.get("equation")
        substrates = _extract_compound_ids(raw.get("substrates", []))
        products = _extract_compound_ids(raw.get("products", []))
        enzymes = list(raw.get("enzymes", []))

        reaction = Reaction(
            id=reaction_id,
            equation=equation,
            substrates=substrates,
            products=products,
            enzymes=enzymes,
        )
        compounds = _build_compounds(substrates, products)
        enzyme_models = _build_enzymes(enzymes)
        parsed_reactions.append(
            ParsedReaction(reaction=reaction, compounds=compounds, enzymes=enzyme_models)
        )

    return parsed_reactions


def _build_compounds(substrates: list[str], products: list[str]) -> list[Compound]:
    """Build unique Compound entries from substrate and product ids."""
    compound_ids = sorted(set(substrates + products))
    return [Compound(id=compound_id) for compound_id in compound_ids]


def _extract_compound_ids(compounds: list[dict] | list[str]) -> list[str]:
    """Extract compound ids from structured compound entries or raw strings."""
    if not compounds:
        return []
    if isinstance(compounds[0], str):
        return list(compounds)
    return [compound["id"] for compound in compounds]


def _build_enzymes(enzymes: list[str]) -> list[Enzyme]:
    """Build Enzyme entries from KEGG enzyme identifiers (EC numbers)."""
    enzyme_ids = sorted(set(enzymes))
    return [Enzyme(id=enzyme_id, ec_number=enzyme_id) for enzyme_id in enzyme_ids]