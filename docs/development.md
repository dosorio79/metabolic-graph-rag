# Development Guide

## Daily Workflow

1. Pull latest changes.
2. Sync environment:
   ```bash
   uv sync
   ```
3. Implement focused changes by component.
4. Run relevant checks/tests.
5. Update docs when behavior changes.

## Project Conventions

- Keep ETL steps separated by stage (`fetch`, `normalize`, `load`).
- Keep graph connection handling centralized.
- Keep API handlers thin and move logic to services.
- Keep Cypher in `backend/app/services/graph_queries.py`, not in route handlers.

## Recommended Task Order

1. Implement reliable ETL ingestion path.
2. Validate graph schema and queries.
3. Maintain backend graph read endpoints.
4. Add retrieval/context builder logic.
5. Add agent tool integrations.

## Minimal Verification Checklist

- `uv run python etl/ingest_kegg_cli.py` succeeds.
- `uv run python scripts/test_neo4j_loader.py` succeeds.
- Neo4j contains expected nodes/relationships.
- Backend app starts without import/runtime errors.
- Retrieval endpoints return expected shapes for known IDs.
- Run backend tests:
  ```bash
  uv run pytest tests/backend
  ```

## Documentation Discipline

When adding features:

- Update `README.md` if usage changes.
- Update docs in `docs/` if architecture/workflow changes.
- Update `docs/openapi.yaml` for API contract changes.
- Add task notes in `docs/Build_tasks/` for milestone-specific instructions.
