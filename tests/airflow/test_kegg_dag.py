from __future__ import annotations

import importlib.util
import sys
from types import ModuleType


_active_dag = None
from pathlib import Path


def _install_airflow_stubs() -> None:
    airflow = ModuleType("airflow")
    operators = ModuleType("airflow.operators")
    python_ops = ModuleType("airflow.operators.python")

    class DummyDag:
        def __init__(self, dag_id, description, start_date, schedule, catchup, params, tags):
            self.dag_id = dag_id
            self.description = description
            self.start_date = start_date
            self.schedule = schedule
            self.catchup = catchup
            self.params = params
            self.tags = tags
            self.task_ids = set()

        def __enter__(self):
            global _active_dag
            _active_dag = self
            return self

        def __exit__(self, exc_type, exc, tb):
            global _active_dag
            _active_dag = None
            return False

    class DummyPythonOperator:
        def __init__(self, task_id, python_callable):
            self.task_id = task_id
            self.python_callable = python_callable
            if _active_dag is not None:
                _active_dag.task_ids.add(task_id)

    def dag_context(*args, **kwargs):
        return DummyDag(*args, **kwargs)

    airflow.DAG = dag_context
    python_ops.PythonOperator = DummyPythonOperator

    sys.modules["airflow"] = airflow
    sys.modules["airflow.operators"] = operators
    sys.modules["airflow.operators.python"] = python_ops


def _load_dag_module():
    _install_airflow_stubs()
    dag_path = Path(__file__).resolve().parents[2] / "airflow" / "dags" / "kegg_ingestion.py"
    spec = importlib.util.spec_from_file_location("kegg_ingestion_dag", dag_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load DAG module from {dag_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kegg_dag_definition():
    module = _load_dag_module()
    dag = module.dag

    assert dag.dag_id == "kegg_ingestion"
    assert dag.schedule == "@daily"
    assert dag.catchup is False
    assert dag.params.get("pathway_id") == "hsa00010"
    assert "ingest_kegg_pathway" in dag.task_ids


def test_resolve_pathway_id_prefers_dag_run_conf():
    module = _load_dag_module()

    class DummyDagRun:
        def __init__(self, conf):
            self.conf = conf

    context = {
        "params": {"pathway_id": "hsa00010"},
        "dag_run": DummyDagRun({"pathway_id": "hsa00020"}),
    }

    assert module._resolve_pathway_id(context) == "hsa00020"
