# Task 2 — Retrieval API on Top of Neo4j

## What You Build

This stage exposes the graph through a clean FastAPI layer.

Architecture:

Neo4j -> FastAPI -> retrieval endpoints

At the end of this task, you can query:

- service health
- compounds
- reactions
- pathways

This stage still stops short of LLM-backed answering.

## Why This Stage Matters

The API is the boundary between graph storage and everything user-facing.

It lets you validate:

- whether the graph model is actually usable
- whether query shapes are stable
- whether later RAG logic is built on trustworthy retrieval

## Prerequisites

- Task 1 and Task 1A completed
- Neo4j populated with graph data

## What To Look At In The Repo

- `backend/app/main.py`
- `backend/app/db/neo4j.py`
- `backend/app/api/routes/`
- `backend/app/services/graph_queries.py`
- `backend/app/schemas/graph.py`

## Core Rule For This Stage

All Cypher stays in:

- `backend/app/services/graph_queries.py`

Route handlers should stay thin and delegate to service functions.

## Steps

### 1. Start the backend

If you want the Docker path:

```bash
docker compose up -d
```

If you want the local Python path:

```bash
uv run python -m backend.app.main
```

### 2. Verify the health endpoint

```bash
curl http://localhost:8000/health
```

Expected result:

- API status is `ok`
- Neo4j status is `ok`

### 3. Verify compound retrieval

```bash
curl http://localhost:8000/compounds/C00036
```

You should see:

- `compound_id`
- `name`
- `consuming_reactions`
- `producing_reactions`

### 4. Verify reaction retrieval

```bash
curl http://localhost:8000/reactions/R00209
```

You should see:

- reaction metadata
- substrates
- products
- enzymes

### 5. Verify pathway retrieval

Use a current local example:

```bash
curl http://localhost:8000/pathways/map00010
```

You should see:

- pathway metadata
- reaction list
- `reaction_count`
- `compound_count`
- `enzyme_count`

### 6. Inspect the API contract

Open:

- `http://localhost:8000/docs`

Read the response models in:

- `backend/app/schemas/graph.py`

## Verification

You have completed this stage when:

- `/health` is green
- `/compounds/{compound_id}` returns structured data
- `/reactions/{reaction_id}` returns structured data
- `/pathways/{pathway_id}` returns structured data
- OpenAPI docs are available

## Current Repo State

The retrieval API and its tests already exist in the repository. Use this task
to understand the service boundaries and verify the graph through an API, not to
reinvent FastAPI basics.

## What You Should Understand Before Moving On

- why retrieval should be validated independently from LLM behavior
- how route handlers, service queries, and response schemas divide ownership
- why stable API contracts make RAG integration easier

## Next Task

Continue to [Task 3](./task3.md) to add graph-grounded RAG on top of retrieval.
