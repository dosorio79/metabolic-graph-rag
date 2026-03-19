# Task 1 — Graph Foundation and Manual Ingestion

## What You Build

The first stage gives you the minimum useful graph system:

KEGG source data -> ETL -> Neo4j

At the end of this task, you can:

- start Neo4j locally
- run the KEGG ingestion CLI
- inspect the resulting graph in Neo4j
- understand the core separation between `fetch`, `normalize`, and `load`

This stage intentionally stops before orchestration, FastAPI, RAG, or frontend
work.

## Why This Stage Matters

Everything else in the project depends on one fact being true: the graph has to
exist and be queryable first.

If this stage is weak, later stages only hide the problem behind APIs, prompts,
or UI.

## Prerequisites

- `uv` installed
- Docker available locally
- the repository cloned
- a local `.env` file copied from `.env.example`

## What To Look At In The Repo

- `etl/fetch/`
- `etl/normalize/`
- `etl/load/`
- `etl/ingest_kegg_cli.py`
- `graph/neo4j_client.py`

## Steps

### 1. Sync the Python environment

```bash
uv sync
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

At minimum, set:

- `APP_NEO4J_URI`
- `APP_NEO4J_USER`
- `APP_NEO4J_PASSWORD`

### 3. Start Neo4j

Use the repository compose file:

```bash
docker compose up -d neo4j
```

Neo4j Browser should be available at `http://localhost:7474`.

### 4. Inspect the ETL entrypoint

Read:

- `etl/ingest_kegg_cli.py`
- `etl/fetch/kegg_api.py`
- `etl/normalize/kegg_pipeline.py`
- `etl/load/neo4j_loader.py`

The tutorial goal here is to understand the pipeline shape:

1. fetch raw KEGG data
2. normalize into domain entities
3. load graph nodes and relationships into Neo4j

### 5. Run ingestion manually

```bash
uv run python etl/ingest_kegg_cli.py
```

Optional output artifact:

```bash
uv run python etl/ingest_kegg_cli.py --output data/normalized/kegg_reactions.json
```

### 6. Inspect the graph

Use Neo4j Browser or Cypher shell and run simple checks such as:

```cypher
MATCH (n) RETURN labels(n), count(*) ORDER BY count(*) DESC;
```

```cypher
MATCH (p:Pathway)-[:HAS_REACTION]->(r:Reaction)
RETURN p.id, p.name, count(r)
ORDER BY p.id;
```

## Verification

You have completed this stage when all of the following are true:

- `uv run python etl/ingest_kegg_cli.py` succeeds
- Neo4j is reachable at `http://localhost:7474`
- the graph contains `Pathway` and `Reaction` nodes
- pathway-to-reaction relationships exist

## Current Repo State

This repository already contains a working ingestion CLI and graph loading path.
Use this task to understand and verify the foundation, not to recreate it from
zero.

## Historical Note

Older project notes described Airflow as part of the first milestone. In the
current repository, orchestration is taught in the next stage and Prefect is the
main active path. Airflow remains archived context only.

## What You Should Understand Before Moving On

- why ETL stages are split across `fetch`, `normalize`, and `load`
- how KEGG-derived identifiers become graph nodes and relationships
- how to confirm that ingestion problems are data/graph problems rather than API
  or UI problems

## Next Task

Continue to [Task 1A](./task1a.md) to enrich the graph and add orchestration.
