from backend.app.schemas.graph import CompoundResponse, PathwayResponse, ReactionResponse


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


def test_compound_response_accepts_reaction_summaries():
    payload = {
        "compound_id": "C00036",
        "name": "Oxaloacetate",
        "consuming_reactions": [{"reaction_id": "R00341", "name": "Reaction A"}],
        "producing_reactions": [{"reaction_id": "R00431", "name": "Reaction B"}],
    }

    response = CompoundResponse(**payload)

    assert response.compound_id == "C00036"
    assert response.consuming_reactions[0].reaction_id == "R00341"
    assert response.producing_reactions[0].reaction_id == "R00431"


def test_reaction_response_accepts_compound_amount_summaries():
    payload = {
        "reaction_id": "R00209",
        "name": "Reaction",
        "equation": "A + B <=> C",
        "definition": "Definition",
        "reversible": True,
        "substrates": [{"compound_id": "C00022", "name": "Pyruvate", "coef": 1.0}],
        "products": [{"compound_id": "C00024", "name": "Acetyl-CoA", "coef": 1.0}],
        "enzymes": ["1.2.1.104"],
    }

    response = ReactionResponse(**payload)

    assert response.reaction_id == "R00209"
    assert response.substrates[0].coef == 1.0
    assert response.products[0].compound_id == "C00024"
    assert response.enzymes == ["1.2.1.104"]
