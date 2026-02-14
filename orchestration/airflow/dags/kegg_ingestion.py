"""Airflow DAG for KEGG ingestion into Neo4j."""

from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from airflow import DAG
from airflow.operators.python import PythonOperator


AIRFLOW_HOME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AIRFLOW_HOME))

from etl.load.neo4j_loader import get_driver, load_reactions
from etl.normalize.kegg_pipeline import ingest_pathway


LOG_PATH = Path(os.getenv("KEGG_INGEST_LOG_PATH", "/opt/airflow/logs/kegg_ingestion_task.log"))


def _write_log(message: str) -> None:
	"""Write a simple log line for debugging outside Airflow logs."""
	LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
	timestamp = datetime.now(tz=timezone.utc).isoformat()
	with LOG_PATH.open("a", encoding="utf-8") as handle:
		handle.write(f"{timestamp} {message}\n")


def _resolve_pathway_id(context: dict[str, object]) -> str:
	"""Resolve the pathway id from DAG params or dag_run conf."""
	params = context.get("params", {}) if isinstance(context.get("params"), dict) else {}
	dag_run = context.get("dag_run")

	pathway_id = params.get("pathway_id", "hsa00010")
	if dag_run and dag_run.conf and "pathway_id" in dag_run.conf:
		pathway_id = dag_run.conf["pathway_id"]
	return pathway_id


def run_kegg_ingestion(**context: object) -> None:
	"""Fetch KEGG reactions and load them into Neo4j."""
	pathway_id = _resolve_pathway_id(context)
	_write_log(f"Starting ingestion for pathway_id={pathway_id}")

	uri = os.getenv("APP_NEO4J_URI", os.getenv("NEO4J_URI", "bolt://localhost:7687"))
	user = os.getenv("APP_NEO4J_USER", os.getenv("NEO4J_USER", "neo4j"))
	password = os.getenv("APP_NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD"))

	driver = get_driver(uri=uri, user=user, password=password)
	try:
		reactions = ingest_pathway(pathway_id)
		_write_log(f"Fetched {len(reactions)} reactions")
		load_reactions(driver, reactions)
		_write_log("Load completed")
	except Exception:
		_write_log("Ingestion failed")
		_write_log(traceback.format_exc())
		raise
	finally:
		driver.close()


with DAG(
	dag_id="kegg_ingestion",
	description="Ingest KEGG pathway reactions into Neo4j",
	start_date=datetime(2026, 2, 12, tzinfo=timezone.utc),
	schedule="@daily",
	catchup=False,
	params={"pathway_id": "hsa00010"},
	tags=["kegg", "neo4j", "etl"],
) as dag:
	PythonOperator(
		task_id="ingest_kegg_pathway",
		python_callable=run_kegg_ingestion,
	)
