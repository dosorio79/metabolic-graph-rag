# Metabolic Graph RAG

[![CI](https://github.com/dosorio79/metabolic-graph-rag/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/dosorio79/metabolic-graph-rag/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/dosorio79/metabolic-graph-rag)](https://github.com/dosorio79/metabolic-graph-rag/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Metabolic Graph RAG builds a metabolic pathway knowledge graph in Neo4j, ingests data from KEGG, and exposes graph-backed retrieval endpoints for backend and RAG workflows.

## Goals

- Ingest pathway and reaction data from KEGG.
- Normalize and load entities into Neo4j.
- Expose graph retrieval endpoints for compounds, reactions, and pathways.
- Support query-driven retrieval for future RAG pipelines.

## Project Layout

```text
metabolic-graph-rag/
├── orchestration/      # Orchestration assets (Prefect + archived Airflow)
├── etl/                # Fetch, normalize, and load pipeline code
├── graph/              # Neo4j client and graph query assets
├── backend/            # FastAPI retrieval API
├── backend/app/rag/    # RAG runtime modules (query understanding, retrieval, context, LLM, pipeline)
├── agents/             # Planner and tool interfaces
├── embeddings/         # Embedding build scripts
├── data/               # Raw and normalized local artifacts
├── docs/               # Build tasks and technical documentation
└── scripts/            # Utility scripts (reset, maintenance)
```

## Tech Stack

- Python 3.12+
- `uv` for dependency and lockfile management
- Neo4j as graph database
- FastAPI + Uvicorn for backend API
- Airflow (Docker image) for scheduled ingestion orchestration

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Set at least:

- `APP_NEO4J_URI`
- `APP_NEO4J_USER`
- `APP_NEO4J_PASSWORD`

### 3. Start Neo4j

Use your preferred method (local Docker, compose, or managed instance).
If using Docker compose in this repo (Neo4j only):

```bash
docker compose up -d
```

To start the archived Airflow stack (optional):

```bash
docker compose -f orchestration/airflow/docker-compose.yml up -d
```

### 4. Run ingestion manually

```bash
uv run python etl/ingest_kegg_cli.py
```

Optional: write results to a JSON file.

```bash
uv run python etl/ingest_kegg_cli.py --output data/normalized/kegg_reactions.json
```

### 5. Start backend API

```bash
uv run uvicorn backend.app.main:app --reload
```

### 6. Test retrieval endpoints

```bash
curl http://localhost:8000/health
curl http://localhost:8000/compounds/C00036
curl http://localhost:8000/reactions/R00209
curl http://localhost:8000/pathways/hsa00010
```

Open interactive docs at `http://localhost:8000/docs`.

## API Endpoints

- `GET /health`: API + Neo4j connectivity status.
- `GET /compounds/{compound_id}`: compound with consuming/producing reactions.
- `GET /reactions/{reaction_id}`: reaction details, substrates/products, enzymes.
- `GET /pathways/{pathway_id}`: pathway metadata, reactions, and summary counts.

## Testing

Run active tests (same filter as CI):

```bash
uv run pytest -m "not archived_airflow"
```

Or use Makefile shortcuts:

```bash
make test-active
make test-backend
make test-etl
make test-airflow
```

Run backend-focused tests only:

```bash
uv run pytest tests/backend
```

Run archived Airflow tests separately (optional):

```bash
uv run pytest tests/airflow
```

CI includes:

- Python test job excluding archived Airflow tests.
- Docker smoke job that boots `neo4j` + `api`, waits for `/health`, and validates retrieval endpoint wiring.

## Documentation

- Project docs index: `docs/README.md`
- OpenAPI spec: `docs/openapi.yaml`
- Task 1 brief: `docs/Build_tasks/task1.md`
- Task 2 brief: `docs/Build_tasks/task2.md`
- Quickstart: `docs/quickstart.md`
- Architecture: `docs/architecture.md`
- Development workflow: `docs/development.md`
- Testing guide: `docs/testing.md`

## Current Status

- KEGG ingestion pipeline is available via CLI.
- Graph retrieval endpoints are implemented in FastAPI.
- Neo4j-backed response models are defined in `backend/app/schemas/graph.py`.
- Task 3 RAG runtime scaffolding is under `backend/app/rag/`; implementation is in progress.

## License

This project is licensed under the MIT License.
See `LICENSE` for full terms.
