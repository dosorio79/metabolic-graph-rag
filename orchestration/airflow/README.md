# Airflow (Archived)

This folder preserves the original Airflow-based orchestration for reference.

Airflow is no longer the primary orchestration tool. New work should use the
Prefect flows in the `flows/` directory.

## Usage (optional)

To start the archived Airflow stack:

```bash
docker compose -f orchestration/airflow/docker-compose.yml up -d
```
