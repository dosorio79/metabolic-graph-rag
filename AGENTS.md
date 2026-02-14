# AGENTS.md

This file defines practical working rules for humans and coding agents collaborating in this repository.

## Scope

Applies to the full repository unless a deeper directory includes its own `AGENTS.md` with more specific instructions.

## Primary Objective

Deliver a reliable metabolic graph ingestion and retrieval platform with clear, incremental implementation:

1. ETL from KEGG
2. Graph persistence in Neo4j
3. Retrieval interfaces for backend and RAG flows
4. API and orchestration layers

## Working Principles

- Keep changes small, testable, and reviewable.
- Prefer explicit code over implicit behavior.
- Preserve separation of concerns: `etl/`, `graph/`, `backend/`, `rag/`, `agents/`.
- Do not mix experimental scripts with production modules.

## Dependency Management

- Use `uv` for Python dependencies.
- Update dependencies with `uv add ...`.
- Keep `pyproject.toml` and `uv.lock` in sync.

## Coding Standards

- Python 3.12+.
- Use type hints in new modules.
- Use clear function names and docstrings for public functions.
- Avoid introducing global mutable state.
- Keep I/O boundaries explicit (network, filesystem, DB).

## ETL Conventions

- `etl/fetch/`: only external-source fetching logic.
- `etl/normalize/`: deterministic parsing/normalization.
- `etl/load/`: graph persistence and Cypher execution.
- `etl/ingest_kegg_cli.py`: orchestration entrypoint for manual runs.

## Graph Conventions

- Centralize Neo4j driver/session handling in `graph/neo4j_client.py`.
- Parameterize Cypher queries (never string-interpolate user input).
- Use `MERGE` for idempotent node/relationship ingestion where appropriate.

## Backend Conventions

- Keep API routing in `backend/app/api/`.
- Put business logic in `backend/app/services/`.
- Keep graph access wrappers isolated in `backend/app/graph/`.

## Validation and Testing

- Add or update tests for behavior changes when test harness exists.
- At minimum, validate:
  - ingestion script runs
  - Neo4j connection succeeds
  - key graph queries return expected shapes

## Documentation

- Update `README.md` for user-facing changes.
- Update `docs/` for architecture or workflow changes.
- Keep examples aligned with actual commands and paths.

## Safety Rules

- Do not delete unrelated files.
- Do not rewrite large sections of existing docs without need.
- Do not commit secrets or real credentials.

## Suggested Delivery Flow

1. Implement minimal vertical slice.
2. Verify manually.
3. Add tests.
4. Document usage and known limitations.
