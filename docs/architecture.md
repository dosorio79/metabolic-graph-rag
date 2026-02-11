# Architecture

## High-Level Flow

```text
KEGG API
  -> etl/fetch
  -> etl/normalize
  -> etl/load
  -> Neo4j
  -> graph queries / retriever
  -> backend API / agents
```

## Components

### `etl/`

- Fetches source data from KEGG.
- Converts raw payloads into normalized entities.
- Loads entities and relationships into Neo4j.

### `graph/`

- Provides graph driver/session access.
- Hosts reusable query definitions.

### `backend/`

- FastAPI entrypoint and request layer.
- Service layer for orchestration and domain logic.
- Graph adapters for read operations.

### `rag/`

- Retrieval logic over graph results.
- Context builder for downstream generation.

### `agents/`

- Planning and tool wiring for agentic workflows.

### `airflow/`

- Scheduling and orchestration of ingestion jobs.

## Data Model (Initial)

- `Compound` nodes
- `Reaction` nodes
- Relationships:
  - `(:Compound)-[:CONSUMED_BY {coef}]->(:Reaction)`
  - `(:Reaction)-[:PRODUCES {coef}]->(:Compound)`

This can be extended later with compounds, enzymes, and gene mappings.
