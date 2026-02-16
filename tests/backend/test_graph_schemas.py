from backend.app.schemas.graph import PathwayResponse


def test_pathway_response_accepts_counts():
    payload = {
        "pathway_id": "hsa00010",
        "name": "Glycolysis",
        "reactions": [{"reaction_id": "R00001", "name": "Reaction"}],
        "reaction_count": 1,
        "compound_count": 2,
        "enzyme_count": 1,
    }

    response = PathwayResponse(**payload)

    assert response.reaction_count == 1
    assert response.compound_count == 2
    assert response.enzyme_count == 1
