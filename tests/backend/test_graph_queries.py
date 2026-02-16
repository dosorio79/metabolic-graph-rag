from __future__ import annotations

from backend.app.services import graph_queries


class DummyRecord:
    def __init__(self, payload):
        self._payload = payload

    def data(self):
        return self._payload


class DummyResult:
    def __init__(self, payload):
        self._payload = payload

    def single(self):
        if self._payload is None:
            return None
        return DummyRecord(self._payload)


class DummySession:
    def __init__(self, payload, captures):
        self._payload = payload
        self._captures = captures

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def run(self, query, **params):
        self._captures.append({"query": query, "params": params})
        return DummyResult(self._payload)


class DummyDriver:
    def __init__(self, payload, captures):
        self._payload = payload
        self._captures = captures
        self.closed = False

    def session(self):
        return DummySession(self._payload, self._captures)

    def close(self):
        self.closed = True


def test_fetch_compound_returns_none_when_missing(monkeypatch):
    captures = []
    driver = DummyDriver(None, captures)
    monkeypatch.setattr(graph_queries, "create_driver", lambda: driver)

    payload = graph_queries.fetch_compound("C404")

    assert payload is None
    assert "MATCH (c:Compound {id: $compound_id})" in captures[0]["query"]
    assert "CONSUMED_BY" in captures[0]["query"]
    assert "PRODUCES" in captures[0]["query"]
    assert captures[0]["params"] == {"compound_id": "C404"}
    assert driver.closed is True


def test_fetch_reaction_normalizes_name_definition_and_equation(monkeypatch):
    captures = []
    driver = DummyDriver(
        {
            "reaction_id": "R00209",
            "name": " pyruvate dehydrogenase; ",
            "definition": "  A   definition; ",
            "equation": "  A + B  =>  C ",
            "reversible": True,
            "substrates": [{"compound_id": "C1", "name": "  A;", "coef": 1.0}],
            "products": [{"compound_id": "C2", "name": " C ", "coef": 1.0}],
            "enzymes": ["1.2.3.4"],
        },
        captures,
    )
    monkeypatch.setattr(graph_queries, "create_driver", lambda: driver)

    payload = graph_queries.fetch_reaction("R00209")

    assert payload is not None
    assert payload["reaction_id"] == "R00209"
    assert payload["name"] == "pyruvate dehydrogenase"
    assert payload["definition"] == "A definition"
    assert payload["equation"] == "A + B => C"
    assert payload["substrates"][0]["name"] == "A"
    assert payload["products"][0]["name"] == "C"
    assert "MATCH (r:Reaction {id: $reaction_id})" in captures[0]["query"]
    assert "CONSUMED_BY" in captures[0]["query"]
    assert "CATALYZED_BY" in captures[0]["query"]
    assert captures[0]["params"] == {"reaction_id": "R00209"}
    assert driver.closed is True


def test_fetch_pathway_returns_counts(monkeypatch):
    captures = []
    driver = DummyDriver(
        {
            "pathway_id": "hsa00010",
            "name": " Glycolysis ;",
            "reactions": [{"reaction_id": "R00001", "name": " Reaction 1 "}],
            "reaction_count": 1,
            "compound_count": 2,
            "enzyme_count": 3,
        },
        captures,
    )
    monkeypatch.setattr(graph_queries, "create_driver", lambda: driver)

    payload = graph_queries.fetch_pathway("hsa00010")

    assert payload is not None
    assert payload["name"] == "Glycolysis"
    assert payload["reaction_count"] == 1
    assert payload["compound_count"] == 2
    assert payload["enzyme_count"] == 3
    assert "MATCH (p:Pathway {id: $pathway_id})" in captures[0]["query"]
    assert "HAS_REACTION" in captures[0]["query"]
    assert "CATALYZED_BY" in captures[0]["query"]
    assert captures[0]["params"] == {"pathway_id": "hsa00010"}
    assert driver.closed is True
