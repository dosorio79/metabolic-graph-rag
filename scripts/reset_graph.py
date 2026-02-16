"""Reset Neo4j graph data and optionally re-apply schema constraints."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
	sys.path.insert(0, str(REPO_ROOT))



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
	from etl.load.neo4j_loader import get_driver

	driver = get_driver()
	try:
		with driver.session() as session:
			count_result = session.run("MATCH (n) RETURN count(n) AS total")
			count_record = count_result.single()
			count = count_record["total"] if count_record else 0
			session.run("MATCH (n) DETACH DELETE n")
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
