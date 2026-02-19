"""Context builder for converting graph data into LLM-ready text."""

from __future__ import annotations

from backend.app.config import get_settings
from backend.app.schemas.rag import RAGRetrieval

_SETTINGS = get_settings()
# Context limits are centralized in settings to keep prompt size predictable.
MAX_REACTIONS = _SETTINGS.rag_context_max_reactions
MAX_COMPOUNDS = _SETTINGS.rag_context_max_compounds
MAX_ENZYMES = _SETTINGS.rag_context_max_enzymes


def _format_reactions(retrieved: RAGRetrieval) -> list[str]:
    # Render only a bounded subset to avoid sending graph dumps to the LLM.
    lines: list[str] = []
    for reaction in retrieved.reactions[:MAX_REACTIONS]:
        reaction_name = f" ({reaction.name})" if reaction.name else ""
        lines.append(f"- {reaction.reaction_id}{reaction_name}")
    overflow = len(retrieved.reactions) - MAX_REACTIONS
    if overflow > 0:
        lines.append(f"- ... {overflow} more reactions")
    return lines


def _format_compounds(retrieved: RAGRetrieval) -> list[str]:
    # Keep compound section parallel to reactions for easier prompt scanning.
    lines: list[str] = []
    for compound in retrieved.compounds[:MAX_COMPOUNDS]:
        compound_name = f" ({compound.name})" if compound.name else ""
        lines.append(f"- {compound.compound_id}{compound_name}")
    overflow = len(retrieved.compounds) - MAX_COMPOUNDS
    if overflow > 0:
        lines.append(f"- ... {overflow} more compounds")
    return lines


def _format_enzymes(retrieved: RAGRetrieval) -> list[str]:
    # EC identifiers are already concise, so formatting is straightforward.
    lines = [f"- {ec}" for ec in retrieved.enzymes[:MAX_ENZYMES]]
    overflow = len(retrieved.enzymes) - MAX_ENZYMES
    if overflow > 0:
        lines.append(f"- ... {overflow} more enzymes")
    return lines


def build_context(retrieved: RAGRetrieval) -> str:
    """Build concise, structured context text for LLM answer generation."""
    interpretation = retrieved.interpretation

    # Lead with compact metadata so the LLM can anchor entity + intent quickly.
    lines = [
        "Metabolic Graph Context",
        "",
        "Interpretation:",
        f"- entity_type: {interpretation.entity_type}",
        f"- intent: {interpretation.intent}",
        f"- entity_id: {retrieved.resolved_entity_id or 'n/a'}",
        f"- entity_name: {interpretation.entity_name or 'n/a'}",
        "",
        "Counts:",
        f"- reactions: {len(retrieved.reactions)}",
        f"- compounds: {len(retrieved.compounds)}",
        f"- enzymes: {len(retrieved.enzymes)}",
    ]

    if retrieved.reactions:
        lines.extend(["", "Reactions:"])
        lines.extend(_format_reactions(retrieved))
    if retrieved.compounds:
        lines.extend(["", "Compounds:"])
        lines.extend(_format_compounds(retrieved))
    if retrieved.enzymes:
        lines.extend(["", "Enzymes (EC):"])
        lines.extend(_format_enzymes(retrieved))

    trace = retrieved.trace
    # Include provenance IDs when available so responses can stay grounded.
    if trace.reaction_ids or trace.compound_ids or trace.pathway_ids or trace.enzyme_ecs:
        lines.extend(
            [
                "",
                "Trace IDs:",
                f"- reaction_ids: {', '.join(trace.reaction_ids) if trace.reaction_ids else 'none'}",
                f"- compound_ids: {', '.join(trace.compound_ids) if trace.compound_ids else 'none'}",
                f"- pathway_ids: {', '.join(trace.pathway_ids) if trace.pathway_ids else 'none'}",
                f"- enzyme_ecs: {', '.join(trace.enzyme_ecs) if trace.enzyme_ecs else 'none'}",
            ]
        )

    return "\n".join(lines)
