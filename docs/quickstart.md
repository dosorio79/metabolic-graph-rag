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

Optional RAG context limits:

- `APP_RAG_CONTEXT_MAX_REACTIONS` (default: `8`)
- `APP_RAG_CONTEXT_MAX_COMPOUNDS` (default: `8`)
- `APP_RAG_CONTEXT_MAX_ENZYMES` (default: `12`)

Optional LLM settings (OpenAI-compatible):

- `APP_LLM_API_BASE` (default: `https://api.openai.com/v1`)
- `APP_LLM_API_KEY`
- `APP_LLM_MODEL` (default: `gpt-4o-mini`)
- `APP_LLM_TEMPERATURE` (default: `0.2`)
- `APP_LLM_MAX_TOKENS` (default: `400`)
- `APP_LLM_TIMEOUT_SECONDS` (default: `30`)

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

## Run ingestion with Prefect (single + batch)

Start Prefect server and worker in separate terminals:

```bash
make prefect-server
make prefect-worker
```

Create deployments:

```bash
make prefect-deploy-all
```

Run single-flow ingestion:

```bash
uv run prefect deployment run 'kegg_pathway_ingestion/local' --params '{"pathway_id":"hsa00010"}'
```

Run batch ingestion:

```bash
uv run prefect deployment run 'kegg_batch_pathway_ingestion/local-batch' --params '{"pathway_ids":["map00010","map00020","map00030","map00051","map00052","map00260","map00280","map00500","map00620","map00630","map00640","map00650"]}'
```

Notes:

- Batch flow accepts `pathway_ids` as a list or string and normalizes input.
- ETL unions reaction ids from module entries, pathway text, and `link/rn` endpoint to improve pathway coverage.

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
uv run python -m backend.app.main
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

## Run tests

Run active suite (same filter used in CI):

```bash
uv run pytest -m "not archived_airflow"
```

Run backend test suite only:

```bash
uv run pytest tests/backend
```

Run archived Airflow tests separately (optional):

```bash
uv run pytest tests/airflow
```
