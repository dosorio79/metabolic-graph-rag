"""Module extraction helpers for KEGG pathway entries."""

import re


def extract_kegg_modules(text: str) -> list[str]:
    """Extract module IDs (Mxxxxx) from a pathway entry blob.

    Args:
        text: Raw KEGG pathway entry text.

    Returns:
        Sorted list of unique module ids.
    """
    # Identify module ids by KEGG naming pattern.
    return sorted(set(re.findall(r'M\d{5}', text)))