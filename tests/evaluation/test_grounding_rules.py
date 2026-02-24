from __future__ import annotations

from types import SimpleNamespace

from evaluation.giskard import model_wrapper
from evaluation.validators.grounding_rules import run_grounding_rules


def test_run_grounding_rules_passes_when_answer_entities_are_retrieved():
    trace = {
        "answer": "Reaction R00010 converts C00022 with enzyme 1.2.3.4.",
        "retrieved_reactions": ["R00010"],
        "retrieved_compounds": ["C00022"],
        "retrieved_enzymes": ["1.2.3.4"],
    }

    result = run_grounding_rules(trace)

    assert result["grounding_passed"] is True
    assert result["failed_tests"] == []


def test_run_grounding_rules_flags_ungrounded_entities():
    trace = {
        "answer": "Reaction R99999 consumes C99999 via enzyme 9.9.9.9.",
        "retrieved_reactions": ["R00010"],
        "retrieved_compounds": ["C00022"],
        "retrieved_enzymes": ["1.2.3.4"],
    }

    result = run_grounding_rules(trace)

    assert result["grounding_passed"] is False
    assert "reaction_grounding" in result["failed_tests"]
    assert "compound_grounding" in result["failed_tests"]
    assert "enzyme_grounding" in result["failed_tests"]


def test_run_grounding_rules_requires_insufficient_context_phrase_when_retrieval_empty():
    trace = {
        "answer": "I need more data.",
        "retrieved_reactions": [],
        "retrieved_compounds": [],
        "retrieved_enzymes": [],
    }

    result = run_grounding_rules(trace)

    assert result["grounding_passed"] is False
    assert "insufficient_context_behavior" in result["failed_tests"]


def test_run_grounding_rules_accepts_insufficient_context_phrase_when_retrieval_empty():
    trace = {
        "answer": "There is insufficient context to answer this from the retrieved graph.",
        "retrieved_reactions": [],
        "retrieved_compounds": [],
        "retrieved_enzymes": [],
    }

    result = run_grounding_rules(trace)

    assert result["grounding_passed"] is True
    assert result["failed_tests"] == []


def test_rag_predict_with_trace_returns_expected_shape(monkeypatch):
    def fake_run_rag_pipeline(_request):
        return SimpleNamespace(
            answer="Grounded answer",
            reactions=[SimpleNamespace(reaction_id="R00010")],
            compounds=[SimpleNamespace(compound_id="C00022")],
            enzymes=["1.2.3.4"],
            context="Context block",
        )

    monkeypatch.setattr(model_wrapper, "run_rag_pipeline", fake_run_rag_pipeline)

    result = model_wrapper.rag_predict_with_trace("How is pyruvate produced?")

    assert result["answer"] == "Grounded answer"
    assert result["retrieved_reactions"] == ["R00010"]
    assert result["retrieved_compounds"] == ["C00022"]
    assert result["retrieved_enzymes"] == ["1.2.3.4"]
    assert result["context"] == "Context block"

