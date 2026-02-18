PYTHON := .venv/bin/python
PYTHONPATH_ROOT := PYTHONPATH=.

.PHONY: test test-active test-ci test-backend test-etl test-airflow prefect-server prefect-deploy prefect-deploy-batch prefect-deploy-all prefect-worker flow flow-batch reset reset-flow

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
	uv run prefect --no-prompt deploy orchestration/prefect/ingestion_flow.py:ingestion_flow --name local --pool default-agent-pool

prefect-deploy-batch:
	uv run prefect --no-prompt deploy orchestration/prefect/ingestion_flow.py:batch_ingestion_flow --name local-batch --pool default-agent-pool

prefect-deploy-all: prefect-deploy prefect-deploy-batch

prefect-worker:
	uv run prefect worker start --pool default-agent-pool

flow:
	$(PYTHON) orchestration/prefect/ingestion_flow.py

flow-batch:
	$(PYTHON) orchestration/prefect/ingestion_flow.py --pathway-ids hsa00010 hsa00020 hsa00030 hsa00620

reset:
	$(PYTHON) scripts/reset_graph.py

reset-flow: reset
	$(PYTHON) orchestration/prefect/ingestion_flow.py
