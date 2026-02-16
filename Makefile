PYTHON := .venv/bin/python
PYTHONPATH_ROOT := PYTHONPATH=.

.PHONY: test test-active test-ci test-backend test-etl test-airflow prefect-server prefect-deploy prefect-worker flow reset reset-flow

test:
	$(PYTHONPATH_ROOT) $(PYTHON) -m pytest

test-active:
	$(PYTHONPATH_ROOT) $(PYTHON) -m pytest -m "not archived_airflow"

test-ci: test-active

test-backend:
	$(PYTHONPATH_ROOT) $(PYTHON) -m pytest tests/backend

test-etl:
	$(PYTHONPATH_ROOT) $(PYTHON) -m pytest tests/etl

test-airflow:
	$(PYTHONPATH_ROOT) $(PYTHON) -m pytest tests/airflow

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
