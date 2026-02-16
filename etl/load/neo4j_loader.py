"""Neo4j loader for metabolic reactions.

Loads parsed KEGG reactions into a metabolic graph.

Graph model:

(:Pathway {id, name})
(:Reaction {id, reversible, name, definition})
(:Compound {id, name})
(:Enzyme {ec})

(:Pathway)-[:HAS_REACTION]->(:Reaction)
(:Compound)-[:CONSUMED_BY {coef}]->(:Reaction)
(:Reaction)-[:PRODUCES {coef}]->(:Compound)
(:Reaction)-[:CATALYZED_BY]->(:Enzyme)
"""

from __future__ import annotations

from typing import Iterable

from neo4j import GraphDatabase

from etl.models.kegg_types import RawReactionRecord
from etl.config import get_settings


# ---------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------
def get_driver(
    uri: str | None = None,
    user: str | None = None,
    password: str | None = None,
):
    """Create a Neo4j driver."""
    settings = get_settings()
    resolved_uri = uri or settings.neo4j_uri
    resolved_user = user or settings.neo4j_user
    resolved_password = password or settings.neo4j_password
    if not resolved_password:
        raise ValueError(
            "Neo4j password is required. Set APP_NEO4J_PASSWORD or pass password."
        )
    return GraphDatabase.driver(resolved_uri, auth=(resolved_user, resolved_password))


# ---------------------------------------------------------------------
# Public loader entry
# ---------------------------------------------------------------------
def load_reactions(driver, reactions: Iterable[RawReactionRecord]) -> None:
    """Load parsed reactions into Neo4j."""
    with driver.session() as session:
        seen: set[str] = set()

        for reaction in reactions:
            reaction_id = reaction.get("reaction_id")
            if not reaction_id or reaction_id in seen:
                continue

            seen.add(reaction_id)
            session.execute_write(_load_single_reaction, reaction)


# ---------------------------------------------------------------------
# Reaction loader
# ---------------------------------------------------------------------
def _load_single_reaction(tx, reaction: RawReactionRecord) -> None:
    """Load one reaction and its compounds."""

    reaction_id = reaction["reaction_id"]
    pathway_id = reaction.get("pathway_id")
    pathway_name = reaction.get("pathway_name")

    reversible = reaction.get("reversible", True)
    name = reaction.get("name")
    definition = reaction.get("definition")

    # --------------------------
    # Pathway
    # --------------------------
    if pathway_id:
        tx.run(
            """
            MERGE (p:Pathway {id: $pid})
            SET p.name = coalesce($pname, p.name)
            """,
            pid=pathway_id,
            pname=pathway_name,
        )

    # --------------------------
    # Reaction
    # --------------------------
    tx.run(
        """
        MERGE (r:Reaction {id: $rid})
        SET r.reversible = $reversible,
            r.name = coalesce($name, r.name),
            r.definition = coalesce($definition, r.definition)
        """,
        rid=reaction_id,
        reversible=reversible,
        name=name,
        definition=definition,
    )

    # --------------------------
    # Pathway relation
    # --------------------------
    if pathway_id:
        tx.run(
            """
            MATCH (p:Pathway {id: $pid})
            MATCH (r:Reaction {id: $rid})
            MERGE (p)-[:HAS_REACTION]->(r)
            """,
            pid=pathway_id,
            rid=reaction_id,
        )

    # --------------------------
    # Substrates
    # --------------------------
    for compound in reaction.get("substrates", []):
        tx.run(
            """
            MERGE (c:Compound {id: $cid})
            SET c.name = coalesce($name, c.name)
            WITH c
            MATCH (r:Reaction {id: $rid})
            MERGE (c)-[rel:CONSUMED_BY]->(r)
            SET rel.coef = $coef
            """,
            cid=compound["id"],
            name=compound.get("name"),
            rid=reaction_id,
            coef=compound.get("coef", 1),
        )

    # --------------------------
    # Products
    # --------------------------
    for compound in reaction.get("products", []):
        tx.run(
            """
            MERGE (c:Compound {id: $cid})
            SET c.name = coalesce($name, c.name)
            WITH c
            MATCH (r:Reaction {id: $rid})
            MERGE (r)-[rel:PRODUCES]->(c)
            SET rel.coef = $coef
            """,
            cid=compound["id"],
            name=compound.get("name"),
            rid=reaction_id,
            coef=compound.get("coef", 1),
        )

    # --------------------------
    # Enzymes
    # --------------------------
    for enzyme_id in reaction.get("enzymes", []):
        tx.run(
            """
            MERGE (e:Enzyme {ec: $ec})
            WITH e
            MATCH (r:Reaction {id: $rid})
            MERGE (r)-[:CATALYZED_BY]->(e)
            """,
            ec=enzyme_id,
            rid=reaction_id,
        )
