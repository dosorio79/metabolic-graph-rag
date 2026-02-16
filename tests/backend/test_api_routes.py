from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_compound_route_strips_id_and_returns_200(monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(compound_id: str):
        captured["compound_id"] = compound_id
        return {
            "compound_id": "C00036",
            "name": "Oxaloacetate",
            "consuming_reactions": [{"reaction_id": "R00001", "name": "Reaction 1"}],
            "producing_reactions": [],
        }

    monkeypatch.setattr("backend.app.api.routes.compounds.fetch_compound", fake_fetch)

    response = client.get("/compounds/ C00036 ")

    assert response.status_code == 200
    assert captured["compound_id"] == "C00036"
    payload = response.json()
    assert payload["compound_id"] == "C00036"
    assert payload["name"] == "Oxaloacetate"


def test_compound_route_returns_404(monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.compounds.fetch_compound", lambda _cid: None)

    response = client.get("/compounds/C404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Compound not found"}


def test_compound_route_whitespace_id_returns_404_and_passes_empty_id(monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(compound_id: str):
        captured["compound_id"] = compound_id
        return None

    monkeypatch.setattr("backend.app.api.routes.compounds.fetch_compound", fake_fetch)

    response = client.get("/compounds/%20%20")

    assert response.status_code == 404
    assert captured["compound_id"] == ""
    assert response.json() == {"detail": "Compound not found"}


def test_reaction_route_returns_200(monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.routes.reactions.fetch_reaction",
        lambda _rid: {
            "reaction_id": "R00209",
            "name": "Reaction",
            "equation": "A + B <=> C",
            "definition": "Reaction definition",
            "reversible": True,
            "substrates": [{"compound_id": "C1", "name": "A", "coef": 1.0}],
            "products": [{"compound_id": "C2", "name": "C", "coef": 1.0}],
            "enzymes": ["1.2.3.4"],
        },
    )

    response = client.get("/reactions/R00209")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reaction_id"] == "R00209"
    assert payload["reversible"] is True
    assert payload["substrates"][0]["coef"] == 1.0


def test_reaction_route_returns_404(monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.reactions.fetch_reaction", lambda _rid: None)

    response = client.get("/reactions/R404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Reaction not found"}


def test_reaction_route_whitespace_id_returns_404_and_passes_empty_id(monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(reaction_id: str):
        captured["reaction_id"] = reaction_id
        return None

    monkeypatch.setattr("backend.app.api.routes.reactions.fetch_reaction", fake_fetch)

    response = client.get("/reactions/%20%20")

    assert response.status_code == 404
    assert captured["reaction_id"] == ""
    assert response.json() == {"detail": "Reaction not found"}


def test_pathway_route_returns_200(monkeypatch):
    monkeypatch.setattr(
        "backend.app.api.routes.pathways.fetch_pathway",
        lambda _pid: {
            "pathway_id": "hsa00010",
            "name": "Glycolysis",
            "reactions": [{"reaction_id": "R00001", "name": "Reaction 1"}],
            "reaction_count": 1,
            "compound_count": 2,
            "enzyme_count": 1,
        },
    )

    response = client.get("/pathways/hsa00010")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pathway_id"] == "hsa00010"
    assert payload["reaction_count"] == 1


def test_pathway_route_returns_404(monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.pathways.fetch_pathway", lambda _pid: None)

    response = client.get("/pathways/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Pathway not found"}


def test_pathway_route_whitespace_id_returns_404_and_passes_empty_id(monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(pathway_id: str):
        captured["pathway_id"] = pathway_id
        return None

    monkeypatch.setattr("backend.app.api.routes.pathways.fetch_pathway", fake_fetch)

    response = client.get("/pathways/%20%20")

    assert response.status_code == 404
    assert captured["pathway_id"] == ""
    assert response.json() == {"detail": "Pathway not found"}


def test_health_route_ok(monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.health.ping", lambda: None)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "api_status": {"status": "ok"},
        "neo4j_status": {"status": "ok"},
    }


def test_health_route_error(monkeypatch):
    def fake_ping() -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr("backend.app.api.routes.health.ping", fake_ping)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "api_status": {"status": "ok"},
        "neo4j_status": {"status": "error", "detail": "db down"},
    }
