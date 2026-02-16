"""Reset Neo4j graph data and optionally re-apply schema constraints."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

from etl.load.neo4j_loader import get_driver


def _apply_schema(driver, schema_path: Path) -> None:
	if not schema_path.exists():
		print(f"Schema file not found: {schema_path}")
		return

	statements = [
		stmt.strip() for stmt in schema_path.read_text().split(";") if stmt.strip()
	]
	with driver.session() as session:
		for statement in statements:
			session.run(statement)


def reset_graph(*, apply_schema: bool, schema_path: Path) -> None:
	load_dotenv()
	driver = get_driver()
	try:
		with driver.session() as session:
			result = session.run(
				"""
				MATCH (n)
				WITH collect(n) AS nodes, count(n) AS total
				UNWIND nodes AS n
				DETACH DELETE n
				RETURN total
				"""
			)
			deleted = result.single()
			count = deleted["total"] if deleted else 0
			print(f"Deleted nodes: {count}")
		if apply_schema:
			_apply_schema(driver, schema_path)
			print("Schema constraints applied")
	finally:
		driver.close()


def main() -> None:
	parser = argparse.ArgumentParser(description="Reset Neo4j graph data.")
	parser.add_argument(
		"--no-schema",
		action="store_true",
		help="Skip re-applying schema constraints.",
	)
	parser.add_argument(
		"--schema-path",
		type=Path,
		default=Path(__file__).resolve().parents[1] / "graph" / "schema.cypher",
		help="Path to schema.cypher file.",
	)
	args = parser.parse_args()

	reset_graph(apply_schema=not args.no_schema, schema_path=args.schema_path)


if __name__ == "__main__":
	main()
