PYTHON := .venv/bin/python

.PHONY: test test-airflow prefect-server prefect-deploy prefect-worker flow reset reset-flow

test:
	$(PYTHON) -m pytest

test-airflow:
	$(PYTHON) -m pytest tests/airflow

prefect-server:
	uv run prefect server start

prefect-deploy:
	uv run prefect deploy -p orchestration/prefect/ingestion_flow.py:ingestion_flow --name local

prefect-worker:
	uv run prefect worker start --pool default-agent-pool

flow:
	$(PYTHON) orchestration/prefect/ingestion_flow.py

reset:
	$(PYTHON) scripts/reset_graph.py

reset-flow: reset
	$(PYTHON) orchestration/prefect/ingestion_flow.py
