"""Neo4j loader for metabolic reactions.

Loads parsed KEGG reactions into a metabolic graph.

Graph model:

(:Compound {id})
(:Reaction {id, reversible})

(:Compound)-[:CONSUMED_BY {coef}]->(:Reaction)
(:Reaction)-[:PRODUCES {coef}]->(:Compound)
"""

from __future__ import annotations

import os
from typing import Iterable

from etl.models.kegg_types import RawReactionRecord

from neo4j import GraphDatabase


def get_driver(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str | None = None,
):
    """Create a Neo4j driver.

    Args:
        uri: Bolt URI for the Neo4j instance.
        user: Neo4j username.
        password: Neo4j password (falls back to APP_NEO4J_PASSWORD env var).

    Raises:
        ValueError: If no password is provided.
    """
    resolved_password = password or os.getenv("APP_NEO4J_PASSWORD")
    if not resolved_password:
        raise ValueError("Neo4j password is required. Set APP_NEO4J_PASSWORD or pass password.")
    return GraphDatabase.driver(uri, auth=(user, resolved_password))


def load_reactions(driver, reactions: Iterable[RawReactionRecord]) -> None:
    """Load parsed reactions into Neo4j."""
    with driver.session() as session:
        for reaction in reactions:
            session.execute_write(_load_single_reaction, reaction)


def _load_single_reaction(tx, reaction: RawReactionRecord) -> None:
    """Load one reaction and its compounds."""
    reaction_id = reaction["reaction_id"]
    pathway_id = reaction.get("pathway_id")
    pathway_name = reaction.get("pathway_name")
    reversible = reaction.get("reversible", True)
    name = reaction.get("name")
    definition = reaction.get("definition")

    if pathway_id:
        tx.run(
            """
            MERGE (p:Pathway {id: $pid})
            SET p.name = $pname
            """,
            pid=pathway_id,
            pname=pathway_name,
        )

    tx.run(
        """
        MERGE (r:Reaction {id: $rid})
        SET r.reversible = $reversible
        SET r.name = $name
        SET r.definition = $definition
        """,
        rid=reaction_id,
        reversible=reversible,
        name=name,
        definition=definition,
    )

    if pathway_id:
        tx.run(
            """
            MERGE (p:Pathway {id: $pid})
            MERGE (p)-[:HAS_REACTION]->(r:Reaction {id: $rid})
            """,
            pid=pathway_id,
            rid=reaction_id,
        )

    for compound in reaction.get("substrates", []):
        tx.run(
            """
            MERGE (c:Compound {id: $cid})
            MERGE (c)-[rel:CONSUMED_BY]->(r:Reaction {id: $rid})
            SET rel.coef = $coef
            """,
            cid=compound["id"],
            rid=reaction_id,
            coef=compound.get("coef", 1),
        )

    for compound in reaction.get("products", []):
        tx.run(
            """
            MERGE (c:Compound {id: $cid})
            MERGE (r:Reaction {id: $rid})-[rel:PRODUCES]->(c)
            SET rel.coef = $coef
            """,
            cid=compound["id"],
            rid=reaction_id,
            coef=compound.get("coef", 1),
        )

    for enzyme_id in reaction.get("enzymes", []):
        tx.run(
            """
            MERGE (e:Enzyme {ec: $ec})
            MERGE (r:Reaction {id: $rid})-[:CATALYZED_BY]->(e)
            """,
            ec=enzyme_id,
            rid=reaction_id,
        )
