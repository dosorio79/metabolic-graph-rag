# Practical Course — Task 1  
## Knowledge Graph Foundation + Airflow ETL Skeleton

---

## Objective

Build the foundational layer of the metabolic Graph-RAG system:

    Bio API → ETL → Neo4j → Query Validation
                         ↑
                      Airflow

At the end of this task, ingestion works both manually and through Airflow, and the graph is queryable in Neo4j.

This task intentionally excludes LLM, FastAPI, and frontend components.

---

## Final Goal

You must be able to:

- Start Neo4j locally
- Ingest metabolic pathway data
- Store pathway and reaction structure in Neo4j
- Run ingestion manually
- Trigger ingestion via Airflow
- Query the resulting graph

---

## Expected Outcome

After completion:

    uv project
        ↓
    Neo4j running
        ↓
    KEGG ingestion script
        ↓
    Airflow DAG triggers ingestion
        ↓
    Graph queries succeed

---

## Deliverables

### D1 — Neo4j running

Neo4j browser accessible at:

    http://localhost:7474

---

### D2 — uv project initialized

Project contains:

    pyproject.toml
    uv.lock

Dependencies installed via uv.

---

### D3 — Ingestion script exists

Script:

    etl/ingest_kegg.py

Must run manually:

    uv run python etl/ingest_kegg.py

---

### D4 — Neo4j graph populated

Graph contains:

- Pathway nodes
- Reaction nodes
- Relationships linking them

---

### D5 — Airflow DAG exists

DAG file:

    airflow/dags/kegg_ingestion.py

And appears in Airflow UI.

---

### D6 — Airflow ingestion works

Running DAG triggers ingestion successfully.

---

### D7 — Validation queries succeed

Queries return data correctly.

---

## Execution Plan

---

### Phase 1 — Initialize uv project

At repo root:

    uv init
    uv add neo4j requests python-dotenv

---

### Phase 2 — Start Neo4j

Run:

    docker run -d \
    --name neo4j-metabolism \
      -p 7474:7474 -p 7687:7687 \
      -e NEO4J_AUTH=neo4j/test \
      neo4j:latest

Login via browser:

    neo4j / test

---

### Phase 3 — Neo4j client setup

Create:

    graph/neo4j_client.py

Basic client:

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "test")
    )

    def run_query(query, params=None):
        with driver.session() as session:
            session.run(query, params or {})

Test connection successfully.

---

### Phase 4 — Fetch KEGG pathway

Test API manually:

    curl https://rest.kegg.jp/get/hsa00010

Add fetch logic in ingestion script.

---

### Phase 5 — Extract reactions

Minimal parsing:

    import re

    def extract_reactions(text):
        reactions = re.findall(r'R\d+', text)
        return list(set(reactions))

Goal: obtain reaction IDs.

---

### Phase 6 — Insert pathway node

Cypher pattern:

    MERGE (p:Pathway {id:$id})
    SET p.name=$name

---

### Phase 7 — Insert reactions

Link reactions to pathway:

    MERGE (r:Reaction {id:$rid})
    MERGE (r)-[:IN_PATHWAY]->(p)

---

### Phase 8 — Minimal metabolites (optional)

Create placeholder metabolite nodes if available.

Detailed metabolite parsing will be improved later.

---

### Phase 9 — Manual ingestion test

Run:

    uv run python etl/ingest_kegg.py

Check graph:

    MATCH (n) RETURN count(n);

---

### Phase 10 — Airflow DAG skeleton

Create:

    airflow/dags/kegg_ingestion.py

Minimal DAG:

    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from datetime import datetime
    import subprocess

    def ingest():
        subprocess.run(["python", "etl/ingest_kegg.py"])

    with DAG(
        dag_id="kegg_ingestion",
        start_date=datetime(2024,1,1),
        schedule_interval=None,
        catchup=False,
    ) as dag:

        PythonOperator(
            task_id="ingest_kegg",
            python_callable=ingest
        )

---

### Phase 11 — Run ingestion via Airflow

Open:

    http://localhost:8080

Trigger DAG manually.

Confirm Neo4j updates.

---

### Phase 12 — Validation queries

Run in Neo4j browser:

List pathways:

    MATCH (p:Pathway) RETURN p;

List reactions:

    MATCH (:Pathway)<-[:IN_PATHWAY]-(r)
    RETURN r LIMIT 10;

Check graph size:

    MATCH (n) RETURN count(n);

---

## Completion Criteria

Task is complete when:

- Neo4j is running
- Ingestion script works manually
- Airflow triggers ingestion
- Graph nodes and relationships exist
- Queries return expected results

---

## What You Gain in Task 1

- Graph modeling basics
- API ingestion patterns
- Neo4j interaction
- Airflow orchestration skeleton
- ETL pipeline discipline

This becomes the foundation for all later tasks.

---

## Next Task Preview

Task 2 — Graph Retrieval API

Next, we will expose graph retrieval via FastAPI:

    Neo4j → FastAPI → retrieval endpoint

No LLM yet — only retrieval.

---
