PYTHON := .venv/bin/python

.PHONY: test test-airflow

test:
	$(PYTHON) -m pytest

test-airflow:
	$(PYTHON) -m pytest tests/airflow
