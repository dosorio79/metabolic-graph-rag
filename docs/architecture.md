# Architecture

## High-Level Flow

```text
KEGG API
  -> etl/fetch
  -> etl/normalize
  -> etl/load
  -> Neo4j
  -> backend/app/services/graph_queries.py
  -> FastAPI retrieval endpoints
  -> clients (frontend / RAG / agents)
```

## Components

### `etl/`

- Fetches source data from KEGG.
- Converts raw payloads into normalized entities.
- Loads entities and relationships into Neo4j.

### `graph/`

- Provides graph driver/session access.
- Hosts reusable query and retrieval assets.

### `backend/`

- FastAPI entrypoint and request layer.
- Route handlers in `backend/app/api/routes/`.
- Query service layer in `backend/app/services/graph_queries.py`.
- Typed response models in `backend/app/schemas/graph.py`.

### `rag/`

- Retrieval logic over graph results.
- Context builder for downstream generation.

### `agents/`

- Planning and tool wiring for agentic workflows.

### `orchestration/airflow/`

- Archived scheduling and orchestration assets (Docker-only runtime).

## Graph Model (Current Retrieval Scope)

Nodes:

- `Compound`
- `Reaction`
- `Pathway`
- `Enzyme`

Relationships:

- `(:Compound)-[:CONSUMED_BY {coef}]->(:Reaction)`
- `(:Reaction)-[:PRODUCES {coef}]->(:Compound)`
- `(:Pathway)-[:HAS_REACTION]->(:Reaction)`
- `(:Reaction)-[:CATALYZED_BY]->(:Enzyme)`

## API Retrieval Surface

- `GET /health`
- `GET /compounds/{compound_id}`
- `GET /reactions/{reaction_id}`
- `GET /pathways/{pathway_id}`

Routes delegate Neo4j access to service functions and return typed Pydantic responses.
