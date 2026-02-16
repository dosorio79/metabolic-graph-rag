"""Neo4j connection helpers."""

from __future__ import annotations

from neo4j import GraphDatabase

from backend.app.config import get_settings


def create_driver():
	settings = get_settings()
	return GraphDatabase.driver(
		settings.neo4j_uri,
		auth=(settings.neo4j_user, settings.neo4j_password),
	)


def ping() -> None:
	driver = create_driver()
	try:
		with driver.session() as session:
			session.run("RETURN 1").single()
	finally:
		driver.close()
