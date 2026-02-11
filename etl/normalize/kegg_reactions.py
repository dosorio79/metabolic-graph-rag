"""Reaction parsing helpers for KEGG modules and reactions."""

import re

from etl.models.kegg_types import CompoundAmount, ParsedReactionFields
from etl.normalize.kegg_enzymes import extract_kegg_enzymes


def extract_kegg_reactions(text: str) -> list[str]:
    """Extract reaction IDs (Rxxxxx) from a module entry blob.

    Args:
        text: Raw KEGG module entry text.

    Returns:
        Sorted list of unique reaction ids.
    """
    # Identify reaction ids by KEGG naming pattern.
    return sorted(set(re.findall(r'R\d{5}', text)))


def parse_reaction_entry(text: str) -> ParsedReactionFields:
    """Parse a KEGG reaction entry into substrates, products, and enzymes.

    Args:
        text: Raw KEGG reaction entry text.

    Returns:
        Parsed reaction fields with empty lists when data is missing.
    """
    equation = _extract_equation(text)
    enzymes = extract_kegg_enzymes(text)

    if not equation:
        return {
            "equation": None,
            "reversible": False,
            "substrates": [],
            "products": [],
            "enzymes": enzymes,
        }

    reversible, substrates, products = _parse_equation(equation)

    return {
        "equation": equation,
        "reversible": reversible,
        "substrates": substrates,
        "products": products,
        "enzymes": sorted(set(enzymes)),
    }


def _extract_equation(text: str) -> str | None:
    """Extract the EQUATION field as a single line string."""
    equation = ""
    capture_equation = False

    for line in text.splitlines():
        if line.startswith("EQUATION"):
            capture_equation = True
            equation = line.replace("EQUATION", "").strip()
            continue

        if capture_equation:
            if line.startswith(" "):
                equation += " " + line.strip()
            else:
                capture_equation = False

    return equation or None


def _parse_equation(equation: str) -> tuple[bool, list[CompoundAmount], list[CompoundAmount]]:
    """Parse stoichiometry and reversibility from a KEGG equation."""
    if "<=>" in equation:
        reversible = True
        left, right = equation.split("<=>", 1)
    elif "=>" in equation:
        reversible = False
        left, right = equation.split("=>", 1)
    else:
        return False, [], []

    substrates = _parse_compound_side(left)
    products = _parse_compound_side(right)
    return reversible, substrates, products


def _parse_compound_side(side: str) -> list[CompoundAmount]:
    """Parse a side of the equation into compound coefficients."""
    compounds: list[CompoundAmount] = []

    for token in side.split("+"):
        match = re.match(r"^\s*(?:(\d+(?:\.\d+)?)\s+)?(C\d{5})\s*$", token)
        if not match:
            continue

        coef_raw, compound_id = match.groups()
        if coef_raw and "." in coef_raw:
            coef: int | float = float(coef_raw)
        elif coef_raw:
            coef = int(coef_raw)
        else:
            coef = 1

        compounds.append({"id": compound_id, "coef": coef})

    return compounds
