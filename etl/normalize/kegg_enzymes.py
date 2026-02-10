"""Enzyme extraction helpers for KEGG entries."""

from __future__ import annotations


def extract_kegg_enzymes(text: str) -> list[str]:
    """Extract enzyme identifiers from a KEGG entry blob.

    Args:
        text: Raw KEGG entry text.

    Returns:
        Sorted list of unique enzyme identifiers.
    """
    enzymes: list[str] = []

    for line in _extract_section_lines(text, "ENZYME"):
        enzymes.extend(line.split())

    return sorted(set(enzymes))


def _extract_section_lines(text: str, section: str) -> list[str]:
    """Collect lines that belong to a KEGG section header.

    Args:
        text: Raw KEGG entry text.
        section: Section header label (e.g., "ENZYME").

    Returns:
        Lines captured for the section with the header label stripped.
    """
    collected: list[str] = []
    capture = False

    for line in text.splitlines():
        if line.startswith(section):
            capture = True
            collected.append(line.replace(section, "").strip())
            continue

        if capture:
            if line.startswith(" "):
                collected.append(line.strip())
            else:
                capture = False

    return collected
