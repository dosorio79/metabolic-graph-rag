import textwrap

from etl.normalize.kegg_enzymes import extract_kegg_enzymes
from etl.normalize.kegg_pipeline import ingest_pathway
from etl.normalize.kegg_reactions import parse_reaction_entry


def test_parse_reaction_entry_reversible_stoichiometry():
    text = textwrap.dedent(
        """
        ENTRY       RTEST01
        EQUATION    2 C00138 + C00024 <=> C00139 + C00022
        ENZYME      1.2.7.1 1.2.7.11
        """
    ).strip()

    parsed = parse_reaction_entry(text)

    assert parsed["equation"] == "2 C00138 + C00024 <=> C00139 + C00022"
    assert parsed["reversible"] is True
    assert parsed["substrates"] == [
        {"id": "C00138", "coef": 2},
        {"id": "C00024", "coef": 1},
    ]
    assert parsed["products"] == [
        {"id": "C00139", "coef": 1},
        {"id": "C00022", "coef": 1},
    ]
    assert parsed["enzymes"] == ["1.2.7.1", "1.2.7.11"]


def test_parse_reaction_entry_irreversible():
    text = textwrap.dedent(
        """
        ENTRY       RTEST02
        EQUATION    C00002 + C00022 => C00008 + C00074
        """
    ).strip()

    parsed = parse_reaction_entry(text)

    assert parsed["reversible"] is False
    assert parsed["substrates"] == [
        {"id": "C00002", "coef": 1},
        {"id": "C00022", "coef": 1},
    ]
    assert parsed["products"] == [
        {"id": "C00008", "coef": 1},
        {"id": "C00074", "coef": 1},
    ]


def test_parse_reaction_entry_decimal_coefficients():
    text = textwrap.dedent(
        """
        ENTRY       RTEST05
        EQUATION    0.5 C00001 + 2 C00002 <=> C00003
        """
    ).strip()

    parsed = parse_reaction_entry(text)

    assert parsed["substrates"] == [
        {"id": "C00001", "coef": 0.5},
        {"id": "C00002", "coef": 2},
    ]
    assert parsed["products"] == [{"id": "C00003", "coef": 1}]


def test_parse_reaction_entry_missing_equation():
    text = textwrap.dedent(
        """
        ENTRY       RTEST03
        ENZYME      2.7.1.1
        """
    ).strip()

    parsed = parse_reaction_entry(text)

    assert parsed["equation"] is None
    assert parsed["substrates"] == []
    assert parsed["products"] == []
    assert parsed["enzymes"] == ["2.7.1.1"]


def test_extract_kegg_enzymes_multiline():
    text = textwrap.dedent(
        """
        ENTRY       RTEST04
        ENZYME      1.1.1.1 2.2.2.2
                    3.3.3.3
        """
    ).strip()

    assert extract_kegg_enzymes(text) == ["1.1.1.1", "2.2.2.2", "3.3.3.3"]


def test_parse_reaction_entry_ignores_unknown_tokens():
    text = textwrap.dedent(
        """
        ENTRY       RTEST06
        EQUATION    C00001 + X00099 <=> C00002
        """
    ).strip()

    parsed = parse_reaction_entry(text)

    assert parsed["substrates"] == [{"id": "C00001", "coef": 1}]
    assert parsed["products"] == [{"id": "C00002", "coef": 1}]


def test_ingest_pathway_skips_missing_equation(monkeypatch):
    def fake_fetch(endpoint: str, entries: str, **_kwargs: object) -> str:
        if entries == "path:demo":
            return "MODULE      M00001\n"
        if entries == "M00001":
            return "REACTION    R00001 R00002\n"
        if entries == "R00001":
            return "EQUATION    C00001 <=> C00002\n"
        if entries == "R00002":
            return "ENZYME      1.1.1.1\n"
        return ""

    monkeypatch.setattr("etl.normalize.kegg_pipeline.fetch_kegg_data", fake_fetch)

    reactions = ingest_pathway("path:demo")

    assert len(reactions) == 1
    assert reactions[0]["reaction_id"] == "R00001"
    assert reactions[0]["equation"] == "C00001 <=> C00002"


def test_ingest_pathway_skips_missing_products(monkeypatch):
    def fake_fetch(endpoint: str, entries: str, **_kwargs: object) -> str:
        if entries == "path:demo":
            return "MODULE      M00001\n"
        if entries == "M00001":
            return "REACTION    R00001 R00002\n"
        if entries == "R00001":
            return "EQUATION    C00001 <=> C00002\n"
        if entries == "R00002":
            return "EQUATION    C00001 <=> X00099\n"
        return ""

    monkeypatch.setattr("etl.normalize.kegg_pipeline.fetch_kegg_data", fake_fetch)

    reactions = ingest_pathway("path:demo")

    assert len(reactions) == 1
    assert reactions[0]["reaction_id"] == "R00001"


def test_ingest_pathway_falls_back_to_pathway_reactions_when_no_modules(monkeypatch):
    def fake_fetch(endpoint: str, entries: str, **_kwargs: object) -> str:
        if entries == "path:demo":
            return "REACTION    R00003 R00004\n"
        if entries == "R00003":
            return "EQUATION    C00010 <=> C00011\n"
        if entries == "R00004":
            return "EQUATION    C00012 => C00013\n"
        return ""

    monkeypatch.setattr("etl.normalize.kegg_pipeline.fetch_kegg_data", fake_fetch)

    reactions = ingest_pathway("path:demo")

    assert len(reactions) == 2
    assert [item["reaction_id"] for item in reactions] == ["R00003", "R00004"]


def test_ingest_pathway_unions_module_and_pathway_reactions(monkeypatch):
    def fake_fetch(endpoint: str, entries: str, **_kwargs: object) -> str:
        if entries == "path:demo":
            return "MODULE      M00001\nREACTION    R00002\n"
        if entries == "M00001":
            return "REACTION    R00001\n"
        if entries == "R00001":
            return "EQUATION    C00001 <=> C00002\n"
        if entries == "R00002":
            return "EQUATION    C00003 => C00004\n"
        return ""

    monkeypatch.setattr("etl.normalize.kegg_pipeline.fetch_kegg_data", fake_fetch)

    reactions = ingest_pathway("path:demo")

    assert [item["reaction_id"] for item in reactions] == ["R00001", "R00002"]


def test_ingest_pathway_collects_reactions_from_link_endpoint(monkeypatch):
    def fake_fetch(endpoint: str, entries: str, **_kwargs: object) -> str:
        if endpoint == "get" and entries == "path:demo":
            return "MODULE      M00001\n"
        if endpoint == "get" and entries == "M00001":
            return ""
        if endpoint == "link/rn" and entries == "path:demo":
            return "path:path:demo\\trn:R12345\\npath:path:demo\\trn:R12346\\n"
        if endpoint == "get" and entries == "R12345":
            return "EQUATION    C00001 <=> C00002\n"
        if endpoint == "get" and entries == "R12346":
            return "EQUATION    C00003 => C00004\n"
        return ""

    monkeypatch.setattr("etl.normalize.kegg_pipeline.fetch_kegg_data", fake_fetch)

    reactions = ingest_pathway("path:demo")

    assert [item["reaction_id"] for item in reactions] == ["R12345", "R12346"]
