from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class Compound:
    """Represents a KEGG compound with its identifier and name."""

    id: str
    name: str | None = None


@dataclass
class Enzyme:
    """Represents a KEGG enzyme with its identifier and EC number."""

    id: str
    ec_number: str
    name: str | None = None


@dataclass
class Reaction:
    """Represents a KEGG reaction with its identifier and equation."""

    id: str
    equation: str | None = None
    substrates: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    enzymes: list[str] = field(default_factory=list)


@dataclass
class ParsedReaction:
    """Typed ingestion unit built from raw pipeline records."""

    reaction: Reaction
    compounds: list[Compound] = field(default_factory=list)
    enzymes: list[Enzyme] = field(default_factory=list)
    
    