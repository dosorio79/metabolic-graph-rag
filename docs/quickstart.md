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
docker compose up -d
```

This compose file starts Neo4j only. Airflow is archived under
`orchestration/airflow/` if you need it.

To start Airflow (optional):

```bash
docker compose -f orchestration/airflow/docker-compose.yml up -d
```

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

## Run backend API

```bash
uv run uvicorn backend.app.main:app --reload
```

Open Swagger UI at `http://localhost:8000/docs`.

## Verify retrieval endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/compounds/C00036
curl http://localhost:8000/reactions/R00209
curl http://localhost:8000/pathways/hsa00010
```

Expected behavior:

- `/health` returns API and Neo4j status objects.
- `/compounds/{compound_id}` returns consuming/producing reaction lists.
- `/reactions/{reaction_id}` returns definition, equation, reversible flag, substrates/products, enzymes.
- `/pathways/{pathway_id}` returns reactions plus `reaction_count`, `compound_count`, and `enzyme_count`.
