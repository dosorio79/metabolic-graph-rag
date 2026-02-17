"""Graph retrieval helpers for Task 3 RAG pipeline.

This module maps a deterministic `RAGInterpretation` to concrete graph-query
calls and returns a normalized retrieval payload for context-building.
"""

from __future__ import annotations

from typing import Any, Callable

from backend.app.schemas.rag import (
    RAGCompoundSummary,
    RAGInterpretation,
    RAGReactionSummary,
    RAGRetrieval,
    RAGTrace,
)
from backend.app.services import graph_queries

RetrieverOutput = RAGRetrieval


def _empty_retrieval(interpretation: RAGInterpretation, resolved_entity_id: str | None) -> RetrieverOutput:
    """Create the baseline retrieval payload with empty collections."""
    return RAGRetrieval(interpretation=interpretation, resolved_entity_id=resolved_entity_id)


def _dedupe_reactions(items: list[dict[str, Any]]) -> list[RAGReactionSummary]:
    """Return unique `{reaction_id, name}` entries preserving first-seen order."""
    seen: set[str] = set()
    deduped: list[RAGReactionSummary] = []
    for item in items:
        reaction_id = item.get("reaction_id")
        if not reaction_id or reaction_id in seen:
            continue
        seen.add(reaction_id)
        deduped.append(RAGReactionSummary(reaction_id=reaction_id, name=item.get("name")))
    return deduped


def _collect_enzymes_from_reactions(reactions: list[RAGReactionSummary]) -> list[str]:
    """Expand reaction summaries into unique sorted enzyme EC identifiers."""
    enzymes: set[str] = set()
    for reaction in reactions:
        reaction_id = reaction.reaction_id
        if not reaction_id:
            continue
        payload = graph_queries.fetch_reaction(reaction_id)
        if not payload:
            continue
        for ec in payload.get("enzymes", []):
            if ec:
                enzymes.add(ec)
    return sorted(enzymes)


def _resolve_entity_id(interpretation: RAGInterpretation) -> str | None:
    """Resolve entity id from interpretation, falling back to name lookups."""
    if interpretation.entity_id:
        return interpretation.entity_id
    if not interpretation.entity_name:
        return None
    # Name lookups are intentionally entity-type specific to keep retrieval
    # deterministic and avoid cross-type collisions.
    if interpretation.entity_type == "compound":
        return graph_queries.lookup_compound_id_by_name(interpretation.entity_name)
    if interpretation.entity_type == "reaction":
        return graph_queries.lookup_reaction_id_by_name(interpretation.entity_name)
    if interpretation.entity_type == "pathway":
        return graph_queries.lookup_pathway_id_by_name(interpretation.entity_name)
    if interpretation.entity_type == "enzyme":
        return interpretation.entity_name
    return None


def _select_compound_reactions(compound_payload: dict[str, Any], intent: str) -> list[RAGReactionSummary]:
    """Pick reaction lists for a compound based on interpreted intent."""
    producing = compound_payload.get("producing_reactions", [])
    consuming = compound_payload.get("consuming_reactions", [])
    if intent == "producers":
        return _dedupe_reactions(producing)
    if intent == "consumers":
        return _dedupe_reactions(consuming)
    return _dedupe_reactions(producing + consuming)


def _handle_compound(interpretation: RAGInterpretation, resolved_entity_id: str) -> RetrieverOutput:
    """Retrieve compound-centric context (compound summary + related reactions)."""
    result = _empty_retrieval(interpretation, resolved_entity_id)
    compound = graph_queries.fetch_compound(resolved_entity_id)
    if not compound:
        return result

    # Keep retrieval payload minimal: one focal compound + relevant reaction set.
    result.compounds = [
        RAGCompoundSummary(compound_id=compound["compound_id"], name=compound.get("name"))
    ]
    result.reactions = _select_compound_reactions(compound, interpretation.intent)
    if interpretation.intent == "participants":
        # Enzyme expansion is opt-in for participant-style questions.
        result.enzymes = _collect_enzymes_from_reactions(result.reactions)
    return result


def _handle_reaction(interpretation: RAGInterpretation, resolved_entity_id: str) -> RetrieverOutput:
    """Retrieve reaction-centric context (reaction + substrates/products/enzymes)."""
    result = _empty_retrieval(interpretation, resolved_entity_id)
    reaction = graph_queries.fetch_reaction(resolved_entity_id)
    if not reaction:
        return result

    result.reactions = [RAGReactionSummary(reaction_id=reaction["reaction_id"], name=reaction.get("name"))]
    result.compounds = [
        RAGCompoundSummary(compound_id=item.get("compound_id"), name=item.get("name"))
        for item in (reaction.get("substrates", []) + reaction.get("products", []))
        if item.get("compound_id")
    ]
    result.enzymes = [ec for ec in reaction.get("enzymes", []) if ec]
    return result


def _handle_pathway(interpretation: RAGInterpretation, resolved_entity_id: str) -> RetrieverOutput:
    """Retrieve pathway-centric context (pathway reaction expansion)."""
    result = _empty_retrieval(interpretation, resolved_entity_id)
    pathway = graph_queries.fetch_pathway(resolved_entity_id)
    if not pathway:
        return result
    result.reactions = _dedupe_reactions(pathway.get("reactions", []))
    return result


def _handle_enzyme(interpretation: RAGInterpretation, resolved_entity_id: str) -> RetrieverOutput:
    """Retrieve enzyme-centric context (enzyme EC + catalyzed reactions)."""
    result = _empty_retrieval(interpretation, resolved_entity_id)
    enzyme = graph_queries.fetch_enzyme(resolved_entity_id)
    if not enzyme:
        return result
    result.enzymes = [resolved_entity_id]
    result.reactions = _dedupe_reactions(enzyme.get("reactions", []))
    return result


def _build_trace(
    interpretation: RAGInterpretation,
    resolved_entity_id: str | None,
    reactions: list[RAGReactionSummary],
    compounds: list[RAGCompoundSummary],
    enzymes: list[str],
) -> RAGTrace:
    """Build trace metadata from normalized retrieval lists."""
    # Trace IDs are used by downstream layers to explain provenance.
    trace = RAGTrace(
        reaction_ids=[item.reaction_id for item in reactions if item.reaction_id],
        compound_ids=[item.compound_id for item in compounds if item.compound_id],
        enzyme_ecs=enzymes,
    )
    if interpretation.entity_type == "pathway" and resolved_entity_id:
        trace.pathway_ids = [resolved_entity_id]
    return trace


def retrieve_graph_context(interpretation: RAGInterpretation) -> RetrieverOutput:
    """Retrieve graph-grounded context for a parsed user interpretation.

    The return payload always includes `reactions`, `compounds`, `enzymes`, and
    `trace` keys, even when retrieval is empty.
    """
    resolved_entity_id = _resolve_entity_id(interpretation)
    if not resolved_entity_id:
        return _empty_retrieval(interpretation, resolved_entity_id)

    # Dispatch keeps each entity-type retrieval path isolated and readable.
    handlers: dict[str, Callable[[RAGInterpretation, str], RetrieverOutput]] = {
        "compound": _handle_compound,
        "reaction": _handle_reaction,
        "pathway": _handle_pathway,
        "enzyme": _handle_enzyme,
    }
    handler = handlers.get(interpretation.entity_type)
    if not handler:
        return _empty_retrieval(interpretation, resolved_entity_id)

    result = handler(interpretation, resolved_entity_id)
    # Trace is always recomputed from the normalized payload to avoid stale IDs.
    trace = _build_trace(
        interpretation=interpretation,
        resolved_entity_id=resolved_entity_id,
        reactions=result.reactions,
        compounds=result.compounds,
        enzymes=result.enzymes,
    )
    result.trace = trace
    return result
