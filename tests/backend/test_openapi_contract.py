from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_openapi_contains_required_paths_and_schemas():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    doc = response.json()

    paths = doc["paths"]
    assert "/health" in paths
    assert "/compounds/{compound_id}" in paths
    assert "/reactions/{reaction_id}" in paths
    assert "/pathways/{pathway_id}" in paths
    assert "/rag/query" in paths

    schemas = doc["components"]["schemas"]
    assert "CompoundResponse" in schemas
    assert "ReactionResponse" in schemas
    assert "PathwayResponse" in schemas
    assert "RAGRequest" in schemas
    assert "RAGResponse" in schemas


def test_openapi_reaction_response_has_required_fields():
    response = client.get("/openapi.json")
    assert response.status_code == 200

    reaction_schema = response.json()["components"]["schemas"]["ReactionResponse"]
    properties = reaction_schema["properties"]

    assert "reaction_id" in properties
    assert "reversible" in properties
    assert "substrates" in properties
    assert "products" in properties
    assert "enzymes" in properties
