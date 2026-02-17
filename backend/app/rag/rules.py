"""Rule configuration for RAG query understanding."""

from __future__ import annotations

import re

from backend.app.schemas.rag import QueryRules

RULES = QueryRules(
    intent_order=("producers", "consumers", "summary", "participants"),
    entity_type_order=("compound", "reaction", "pathway", "enzyme"),
    intent_patterns={
        "producers": (
            "how is",
            "produced",
            "produce",
            "generated",
            "made from",
            "synthesized",
            "forms",
            "formation",
        ),
        "consumers": (
            "consume",
            "consumed",
            "uses",
            "used by",
            "utilize",
            "degrade",
            "catabol",
            "break down",
        ),
        "participants": (
            "participants",
            "participate",
            "reactants",
            "products",
            "substrates",
            "involved in",
            "enzyme",
            "enzymes",
            "ec ",
            "ec:",
            "cataly",
            "act on",
        ),
        "summary": (
            "what is",
            "tell me about",
            "describe",
            "overview",
            "summary",
        ),
        "unknown": (),
    },
    entity_type_hints={
        "compound": ("compound", "metabolite"),
        "reaction": ("reaction",),
        "pathway": ("pathway",),
        "enzyme": ("enzyme", "enzymes", "ec ", "ec:"),
        "unknown": (),
    },
    name_patterns=(
        re.compile(
            r"\bhow is (?P<name>[a-z0-9][a-z0-9 -]*[a-z0-9]) (?:produced|generated|made|synthesized)\b"
        ),
        re.compile(
            r"\b(?:consume|consumes|consumed|use|uses|used|utilize|utilizes|degrade|degrades|catabolize|catabolizes|break down) (?P<name>[a-z0-9][a-z0-9 -]*[a-z0-9])\b"
        ),
        re.compile(
            r"\b(?:act on|acts on|catalyze|catalyzes|catalyse|catalyses) (?P<name>[a-z0-9][a-z0-9 -]*[a-z0-9])\b"
        ),
        re.compile(r"\b(?:of|for|on|in|about) (?P<name>[a-z0-9][a-z0-9 -]*[a-z0-9])\??$"),
    ),
    stopwords={"a", "an", "the", "compound", "reaction", "pathway", "enzyme", "enzymes", "metabolite"},
    compound_id_re=re.compile(r"\b(C\d{5})\b", re.IGNORECASE),
    reaction_id_re=re.compile(r"\b(R\d{5})\b", re.IGNORECASE),
    pathway_id_re=re.compile(r"\b(?:map\d{5}|[a-z]{2,4}\d{5})\b", re.IGNORECASE),
    enzyme_ec_re=re.compile(r"\b(?:ec[:\s]*)?(\d+\.\d+\.\d+\.\d+)\b", re.IGNORECASE),
)
