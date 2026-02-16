from etl.normalize.name_utils import normalize_name


def test_normalize_name_collapses_whitespace():
    assert normalize_name("  Alpha   Beta  ") == "Alpha Beta"


def test_normalize_name_strips_trailing_semicolon():
    assert normalize_name("Gamma;") == "Gamma"


def test_normalize_name_empty_returns_none():
    assert normalize_name("   ") is None
