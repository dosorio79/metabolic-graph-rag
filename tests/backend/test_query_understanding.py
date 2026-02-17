from __future__ import annotations

import pytest

from backend.app.rag.query_understanding import classify_question, classify_question_with_debug
from backend.app.rag.utils import format_classification_debug


@pytest.mark.parametrize(
    "question,expected",
    [
        (
            "How is pyruvate produced?",
            {"intent": "producers", "entity_type": "compound", "entity_name": "pyruvate"},
        ),
        (
            "What reactions consume oxaloacetate?",
            {"intent": "consumers", "entity_type": "compound", "entity_name": "oxaloacetate"},
        ),
        (
            "Which enzymes act on glucose?",
            {"intent": "participants", "entity_type": "compound", "entity_name": "glucose"},
        ),
        (
            "Show reaction R00209 participants",
            {"intent": "participants", "entity_type": "reaction", "entity_id": "R00209"},
        ),
        (
            "Describe pathway map00010",
            {"intent": "summary", "entity_type": "pathway", "entity_id": "map00010"},
        ),
        (
            "Tell me about compound C00022",
            {"intent": "summary", "entity_type": "compound", "entity_id": "C00022"},
        ),
    ],
)
def test_classify_question_core_cases(question, expected):
    interpretation = classify_question(question)

    assert interpretation.intent == expected["intent"]
    assert interpretation.entity_type == expected["entity_type"]

    if "entity_name" in expected:
        assert interpretation.entity_name == expected["entity_name"]
    if "entity_id" in expected:
        assert interpretation.entity_id == expected["entity_id"]

    assert 0.0 <= interpretation.confidence <= 1.0


def test_classify_question_handles_empty_input():
    interpretation = classify_question("   ")

    assert interpretation.intent == "unknown"
    assert interpretation.entity_type == "unknown"
    assert interpretation.entity_id is None
    assert interpretation.entity_name is None
    assert interpretation.confidence == 0.0


def test_classify_question_promotes_entity_only_to_summary():
    interpretation = classify_question("C00031")

    assert interpretation.intent == "summary"
    assert interpretation.entity_type == "compound"
    assert interpretation.entity_id == "C00031"
    assert interpretation.confidence > 0.0


def test_classify_question_supports_enzyme_entity_type():
    interpretation = classify_question("Tell me about enzyme EC 1.2.1.104")

    assert interpretation.intent == "summary"
    assert interpretation.entity_type == "enzyme"
    assert interpretation.entity_id == "1.2.1.104"
    assert interpretation.confidence > 0.0


def test_classify_question_with_debug_reports_matched_rules():
    interpretation, debug = classify_question_with_debug("How is pyruvate produced?")

    assert interpretation.intent == "producers"
    assert interpretation.entity_type == "compound"
    assert debug["matched_intent_rule"] == "how is"
    assert debug["extracted_entity_name"] == "pyruvate"
    assert debug["matched_name_rule"] is not None
    assert debug["intent_before_promotion"] == "producers"
    assert debug["intent_after_promotion"] == "producers"


def test_format_classification_debug_produces_readable_output():
    _, debug = classify_question_with_debug("C00031")
    output = format_classification_debug(debug)

    assert output.startswith("Query understanding debug:")
    assert "intent_after_promotion: summary" in output
    assert "entity_id_from_id: C00031" in output
