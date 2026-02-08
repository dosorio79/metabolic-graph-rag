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

- `NEO4J_URI` (example: `bolt://localhost:7687`)
- `NEO4J_USER` (example: `neo4j`)
- `NEO4J_PASSWORD`

## Start services

```bash
docker compose up -d
```

If Airflow uses a separate compose file:

```bash
docker compose -f airflow/docker-compose.yaml up -d
```

## Run ingestion manually

```bash
uv run python etl/ingest_kegg.py
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
