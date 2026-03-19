from __future__ import annotations

import pytest

from backend.app.schemas.rag import RAGInterpretation, RAGResponse, RAGTrace


pytestmark = pytest.mark.anyio


async def test_compound_route_strips_id_and_returns_200(api_client, monkeypatch):
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

    response = await api_client.get("/compounds/ C00036 ")

    assert response.status_code == 200
    assert captured["compound_id"] == "C00036"
    payload = response.json()
    assert payload["compound_id"] == "C00036"
    assert payload["name"] == "Oxaloacetate"


async def test_compound_route_returns_404(api_client, monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.compounds.fetch_compound", lambda _cid: None)

    response = await api_client.get("/compounds/C404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Compound not found"}


async def test_compound_route_whitespace_id_returns_404_and_passes_empty_id(api_client, monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(compound_id: str):
        captured["compound_id"] = compound_id
        return None

    monkeypatch.setattr("backend.app.api.routes.compounds.fetch_compound", fake_fetch)

    response = await api_client.get("/compounds/%20%20")

    assert response.status_code == 404
    assert captured["compound_id"] == ""
    assert response.json() == {"detail": "Compound not found"}


async def test_reaction_route_returns_200(api_client, monkeypatch):
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

    response = await api_client.get("/reactions/R00209")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reaction_id"] == "R00209"
    assert payload["reversible"] is True
    assert payload["substrates"][0]["coef"] == 1.0


async def test_reaction_route_returns_404(api_client, monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.reactions.fetch_reaction", lambda _rid: None)

    response = await api_client.get("/reactions/R404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Reaction not found"}


async def test_reaction_route_whitespace_id_returns_404_and_passes_empty_id(api_client, monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(reaction_id: str):
        captured["reaction_id"] = reaction_id
        return None

    monkeypatch.setattr("backend.app.api.routes.reactions.fetch_reaction", fake_fetch)

    response = await api_client.get("/reactions/%20%20")

    assert response.status_code == 404
    assert captured["reaction_id"] == ""
    assert response.json() == {"detail": "Reaction not found"}


async def test_pathway_route_returns_200(api_client, monkeypatch):
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

    response = await api_client.get("/pathways/hsa00010")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pathway_id"] == "hsa00010"
    assert payload["reaction_count"] == 1


async def test_pathway_route_returns_404(api_client, monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.pathways.fetch_pathway", lambda _pid: None)

    response = await api_client.get("/pathways/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Pathway not found"}


async def test_pathway_route_whitespace_id_returns_404_and_passes_empty_id(api_client, monkeypatch):
    captured: dict[str, str] = {}

    def fake_fetch(pathway_id: str):
        captured["pathway_id"] = pathway_id
        return None

    monkeypatch.setattr("backend.app.api.routes.pathways.fetch_pathway", fake_fetch)

    response = await api_client.get("/pathways/%20%20")

    assert response.status_code == 404
    assert captured["pathway_id"] == ""
    assert response.json() == {"detail": "Pathway not found"}


async def test_health_route_ok(api_client, monkeypatch):
    monkeypatch.setattr("backend.app.api.routes.health.ping", lambda: None)

    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "api_status": {"status": "ok"},
        "neo4j_status": {"status": "ok"},
    }


async def test_health_route_error(api_client, monkeypatch):
    def fake_ping() -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr("backend.app.api.routes.health.ping", fake_ping)

    response = await api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "api_status": {"status": "ok"},
        "neo4j_status": {"status": "error", "detail": "db down"},
    }


async def test_rag_query_route_returns_200(api_client, monkeypatch):
    captured: dict[str, str] = {}

    def fake_run_rag_pipeline(request):
        captured["question"] = request.question
        return RAGResponse(
            answer="Pyruvate is produced by reaction R1.",
            interpretation=RAGInterpretation(
                entity_type="compound",
                entity_id="C00022",
                entity_name="pyruvate",
                intent="producers",
                confidence=0.9,
            ),
            context="Metabolic Graph Context",
            reactions=[{"reaction_id": "R1", "name": "Reaction 1"}],
            compounds=[{"compound_id": "C00022", "name": "Pyruvate"}],
            enzymes=["1.2.3.4"],
            trace=RAGTrace(reaction_ids=["R1"], compound_ids=["C00022"], enzyme_ecs=["1.2.3.4"]),
        )

    monkeypatch.setattr("backend.app.api.routes.rag.run_rag_pipeline", fake_run_rag_pipeline)

    response = await api_client.post("/rag/query", json={"question": " How is pyruvate produced? "})

    assert response.status_code == 200
    assert captured["question"] == "How is pyruvate produced?"
    payload = response.json()
    assert payload["answer"] == "Pyruvate is produced by reaction R1."
    assert payload["interpretation"]["entity_type"] == "compound"
    assert payload["reactions"][0]["reaction_id"] == "R1"


async def test_rag_query_route_rejects_empty_question(api_client):
    response = await api_client.post("/rag/query", json={"question": "   "})

    assert response.status_code == 422
