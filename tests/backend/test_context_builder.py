from __future__ import annotations

from backend.app.rag.context_builder import build_context
from backend.app.schemas.rag import (
    RAGCompoundSummary,
    RAGInterpretation,
    RAGReactionSummary,
    RAGRetrieval,
    RAGTrace,
)


def test_build_context_includes_key_sections():
    retrieval = RAGRetrieval(
        interpretation=RAGInterpretation(
            entity_type="compound",
            entity_id="C00022",
            entity_name="pyruvate",
            intent="producers",
            confidence=0.9,
        ),
        resolved_entity_id="C00022",
        reactions=[RAGReactionSummary(reaction_id="R1", name="rxn1")],
        compounds=[RAGCompoundSummary(compound_id="C00022", name="pyruvate")],
        enzymes=["1.2.3.4"],
        trace=RAGTrace(reaction_ids=["R1"], compound_ids=["C00022"], enzyme_ecs=["1.2.3.4"]),
    )

    context = build_context(retrieval)

    assert "Metabolic Graph Context" in context
    assert "Interpretation:" in context
    assert "Counts:" in context
    assert "Reactions:" in context
    assert "Compounds:" in context
    assert "Enzymes (EC):" in context
    assert "Trace IDs:" in context
    assert "- R1 (rxn1)" in context
    assert "- C00022 (pyruvate)" in context
    assert "- 1.2.3.4" in context


def test_build_context_truncates_long_lists():
    retrieval = RAGRetrieval(
        interpretation=RAGInterpretation(
            entity_type="pathway",
            entity_id="map00010",
            entity_name="glycolysis",
            intent="summary",
            confidence=0.8,
        ),
        resolved_entity_id="map00010",
        reactions=[RAGReactionSummary(reaction_id=f"R{i:05d}") for i in range(12)],
        compounds=[RAGCompoundSummary(compound_id=f"C{i:05d}") for i in range(10)],
        enzymes=[f"1.1.1.{i}" for i in range(20)],
    )

    context = build_context(retrieval)

    assert "... 4 more reactions" in context
    assert "... 2 more compounds" in context
    assert "... 8 more enzymes" in context


def test_build_context_empty_payload_is_still_informative():
    retrieval = RAGRetrieval(
        interpretation=RAGInterpretation(entity_type="unknown", intent="unknown", confidence=0.0)
    )

    context = build_context(retrieval)

    assert "Metabolic Graph Context" in context
    assert "- reactions: 0" in context
    assert "- compounds: 0" in context
    assert "- enzymes: 0" in context
