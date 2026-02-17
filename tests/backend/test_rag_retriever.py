from __future__ import annotations

from backend.app.rag import retriever
from backend.app.schemas.rag import RAGInterpretation


def test_retrieve_graph_context_compound_producers(monkeypatch):
    monkeypatch.setattr(retriever.graph_queries, "lookup_compound_id_by_name", lambda _: "C00022")
    monkeypatch.setattr(
        retriever.graph_queries,
        "fetch_compound",
        lambda _: {
            "compound_id": "C00022",
            "name": "pyruvate",
            "producing_reactions": [{"reaction_id": "R1", "name": "rxn1"}],
            "consuming_reactions": [{"reaction_id": "R2", "name": "rxn2"}],
        },
    )

    result = retriever.retrieve_graph_context(
        RAGInterpretation(entity_type="compound", entity_name="pyruvate", intent="producers", confidence=0.9)
    )

    assert result.resolved_entity_id == "C00022"
    assert [item.reaction_id for item in result.reactions] == ["R1"]
    assert [item.compound_id for item in result.compounds] == ["C00022"]
    assert result.enzymes == []
    assert result.trace.reaction_ids == ["R1"]
    assert result.trace.compound_ids == ["C00022"]


def test_retrieve_graph_context_compound_participants_collects_enzymes(monkeypatch):
    monkeypatch.setattr(
        retriever.graph_queries,
        "fetch_compound",
        lambda _: {
            "compound_id": "C00031",
            "name": "glucose",
            "producing_reactions": [{"reaction_id": "R10", "name": "rxn10"}],
            "consuming_reactions": [{"reaction_id": "R20", "name": "rxn20"}],
        },
    )
    reaction_payloads = {
        "R10": {"reaction_id": "R10", "enzymes": ["1.1.1.1", "2.2.2.2"]},
        "R20": {"reaction_id": "R20", "enzymes": ["2.2.2.2", "3.3.3.3"]},
    }
    monkeypatch.setattr(retriever.graph_queries, "fetch_reaction", lambda reaction_id: reaction_payloads[reaction_id])

    result = retriever.retrieve_graph_context(
        RAGInterpretation(entity_type="compound", entity_id="C00031", intent="participants", confidence=0.8)
    )

    assert [item.reaction_id for item in result.reactions] == ["R10", "R20"]
    assert result.enzymes == ["1.1.1.1", "2.2.2.2", "3.3.3.3"]
    assert result.trace.enzyme_ecs == ["1.1.1.1", "2.2.2.2", "3.3.3.3"]


def test_retrieve_graph_context_reaction(monkeypatch):
    monkeypatch.setattr(
        retriever.graph_queries,
        "fetch_reaction",
        lambda _: {
            "reaction_id": "R00209",
            "name": "reaction name",
            "substrates": [{"compound_id": "C1", "name": "A"}],
            "products": [{"compound_id": "C2", "name": "B"}],
            "enzymes": ["1.2.3.4"],
        },
    )

    result = retriever.retrieve_graph_context(
        RAGInterpretation(entity_type="reaction", entity_id="R00209", intent="participants", confidence=0.9)
    )

    assert [item.reaction_id for item in result.reactions] == ["R00209"]
    assert [item.compound_id for item in result.compounds] == ["C1", "C2"]
    assert result.enzymes == ["1.2.3.4"]


def test_retrieve_graph_context_enzyme(monkeypatch):
    monkeypatch.setattr(
        retriever.graph_queries,
        "fetch_enzyme",
        lambda _: {
            "enzyme_ec": "1.2.1.104",
            "reactions": [{"reaction_id": "R100", "name": "rxn100"}],
        },
    )

    result = retriever.retrieve_graph_context(
        RAGInterpretation(entity_type="enzyme", entity_id="1.2.1.104", intent="summary", confidence=0.8)
    )

    assert result.enzymes == ["1.2.1.104"]
    assert [item.reaction_id for item in result.reactions] == ["R100"]
    assert result.trace.enzyme_ecs == ["1.2.1.104"]


def test_retrieve_graph_context_unknown_returns_empty():
    result = retriever.retrieve_graph_context(
        RAGInterpretation(entity_type="unknown", entity_id=None, entity_name=None, intent="unknown", confidence=0.0)
    )

    assert result.reactions == []
    assert result.compounds == []
    assert result.enzymes == []
