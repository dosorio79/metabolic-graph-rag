from backend.app.services.name_utils import normalize_name_fields


def test_normalize_name_fields_handles_nested_payloads():
    payload = {
        "name": " Example  Name; ",
        "pathway_name": "  Glycolysis ",
        "definition": "  A   definition; ",
        "equation": "  A + B  =>  C ",
        "meta": {"other": "keep", "name": " Inner  Name  "},
        "items": [{"name": "  Item  One "}, {"name": None}],
    }

    normalized = normalize_name_fields(payload)

    assert normalized["name"] == "Example Name"
    assert normalized["pathway_name"] == "Glycolysis"
    assert normalized["definition"] == "A definition"
    assert normalized["equation"] == "A + B => C"
    assert normalized["meta"]["other"] == "keep"
    assert normalized["meta"]["name"] == "Inner Name"
    assert normalized["items"][0]["name"] == "Item One"
    assert normalized["items"][1]["name"] is None
