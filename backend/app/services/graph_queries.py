"""Graph query service helpers."""

from __future__ import annotations

from typing import Any

from backend.app.db.neo4j import create_driver
from backend.app.services.name_utils import normalize_name_fields


def normalize_response_names(payload: Any) -> Any:
	return normalize_name_fields(payload)


def fetch_compound(compound_id: str) -> dict | None:
	query = """
	MATCH (c:Compound {id: $compound_id})
	CALL {
		WITH c
		MATCH (c)-[:CONSUMED_BY]->(r:Reaction)
		WITH r
		ORDER BY r.id
		RETURN collect({reaction_id: r.id, name: r.name}) AS consuming_reactions
	}
	CALL {
		WITH c
		MATCH (c)<-[:PRODUCES]-(r:Reaction)
		WITH r
		ORDER BY r.id
		RETURN collect({reaction_id: r.id, name: r.name}) AS producing_reactions
	}
	RETURN c.id AS compound_id,
		   c.name AS name,
		   consuming_reactions,
		   producing_reactions
	"""
	driver = create_driver()
	try:
		with driver.session() as session:
			record = session.run(query, compound_id=compound_id).single()
			if not record:
				return None
			payload = record.data()
			return normalize_response_names(payload)
	finally:
		driver.close()

def fetch_reaction(reaction_id: str) -> dict | None:
	query = """
	MATCH (r:Reaction {id: $reaction_id})
	CALL {
		WITH r
		MATCH (c:Compound)-[rel:CONSUMED_BY]->(r)
		WITH c, rel
		ORDER BY c.id
		RETURN collect({compound_id: c.id, name: c.name, coef: rel.coef}) AS substrates
	}
	CALL {
		WITH r
		MATCH (r)-[rel:PRODUCES]->(c:Compound)
		WITH c, rel
		ORDER BY c.id
		RETURN collect({compound_id: c.id, name: c.name, coef: rel.coef}) AS products
	}
	CALL {
		WITH r
		MATCH (r)-[:CATALYZED_BY]->(e:Enzyme)
		WITH e
		ORDER BY e.ec
		RETURN collect(e.ec) AS enzymes
	}
	RETURN r.id AS reaction_id,
		   r.name AS name,
		   r.definition AS definition,
		   r.equation AS equation,
		   r.reversible AS reversible,
		   substrates,
		   products,
		   enzymes
	"""
	driver = create_driver()
	try:
		with driver.session() as session:
			record = session.run(query, reaction_id=reaction_id).single()
			if not record:
				return None
			payload = record.data()
			return normalize_response_names(payload)
	finally:
		driver.close()
  
def fetch_pathway(pathway_id: str) -> dict | None:
	query = """
	MATCH (p:Pathway {id: $pathway_id})
	CALL {
		WITH p
		MATCH (p)-[:HAS_REACTION]->(r:Reaction)
		WITH r
		ORDER BY r.id
		RETURN collect({reaction_id: r.id, name: r.name}) AS reactions
	}
	CALL {
		WITH p
		MATCH (p)-[:HAS_REACTION]->(r:Reaction)
		RETURN count(DISTINCT r) AS reaction_count
	}
	CALL {
		WITH p
		MATCH (p)-[:HAS_REACTION]->(r:Reaction)
		OPTIONAL MATCH (r)-[:PRODUCES|CONSUMED_BY]-(c:Compound)
		RETURN count(DISTINCT c) AS compound_count
	}
	CALL {
		WITH p
		MATCH (p)-[:HAS_REACTION]->(r:Reaction)
		OPTIONAL MATCH (r)-[:CATALYZED_BY]->(e:Enzyme)
		RETURN count(DISTINCT e) AS enzyme_count
	}
	RETURN p.id AS pathway_id,
	       p.name AS name,
	       reactions,
	       reaction_count,
	       compound_count,
	       enzyme_count
	"""
	driver = create_driver()
	try:
		with driver.session() as session:
			record = session.run(query, pathway_id=pathway_id).single()
			if not record:
				return None
			payload = record.data()
			return normalize_response_names(payload)
	finally:
		driver.close()
