# Testing Guide

## Test Layout

- `tests/backend/`: API routes, response schemas, query service helpers, OpenAPI contract checks.
- `tests/etl/`: KEGG parsing and normalization behavior.
- `tests/airflow/`: archived Airflow DAG coverage.

## Local Commands

Run active suite (default for day-to-day work and CI):

```bash
uv run pytest -m "not archived_airflow"
```

Run all backend tests:

```bash
uv run pytest tests/backend
```

Run ETL tests:

```bash
uv run pytest tests/etl
```

Run archived Airflow tests explicitly:

```bash
uv run pytest tests/airflow
```

## Pytest Configuration

- `pytest.ini` sets `--import-mode=importlib` to avoid module-name collisions between files with the same basename.
- `pytest.ini` defines marker `archived_airflow` to keep archived Airflow tests out of the default CI path.

## CI Coverage

Workflow: `.github/workflows/ci.yml`

- `tests` job:
  - installs dependencies with `uv sync --frozen`
  - runs `uv run pytest -m "not archived_airflow"`
- `docker-smoke` job:
  - builds and starts `neo4j` + `api` via `docker compose`
  - waits for `/health` to report Neo4j status `ok`
  - validates retrieval endpoint wiring (`/compounds/C00036` must return `200` or `404`)
  - tears down containers and volumes

## Expected Endpoint Test Behavior

- Retrieval endpoints:
  - `200` when entity exists
  - `404` when entity is missing
- Health endpoint:
  - always returns `200`
  - embeds Neo4j status inside payload (`ok` or `error`)
