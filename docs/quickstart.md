# Quickstart

## Prerequisites

- Python 3.12+
- `uv` installed
- Docker (recommended for local Neo4j/Airflow)

## Setup

```bash
uv sync
cp .env.example .env
```

Set `.env` values for Neo4j:

Container settings:

- `NEO4J_AUTH` (example: `neo4j/testtest`)
- `NEO4J_dbms_default__database` (example: `neo4j`)

App/client settings:

- `APP_NEO4J_URI` (example: `bolt://localhost:7687`)
- `APP_NEO4J_USER` (example: `neo4j`)
- `APP_NEO4J_PASSWORD`

Set Airflow admin credentials (used by the Airflow Docker image on first boot):

- `AIRFLOW_ADMIN_USERNAME`
- `AIRFLOW_ADMIN_PASSWORD`

## Start services

```bash
docker compose -f orchestration/airflow/docker-compose.yml up -d
```

This single compose file starts Neo4j and Airflow together (Airflow runs from the
official `apache/airflow` image). Airflow is archived under `orchestration/airflow/`.

Airflow UI: `http://localhost:8080`

## Run ingestion manually

```bash
uv run python etl/ingest_kegg_cli.py
```

Optional: write the raw reactions to disk.

```bash
uv run python etl/ingest_kegg_cli.py --output data/normalized/kegg_reactions.json
```

## Load reactions into Neo4j

```bash
uv run python scripts/test_neo4j_loader.py
```

## Verify graph data

Use Neo4j Browser at `http://localhost:7474` and run a basic query:

```cypher
MATCH (n) RETURN labels(n), count(*) LIMIT 10;
```

## Run backend (skeleton)

```bash
uv run uvicorn backend.app.main:app --reload
```
