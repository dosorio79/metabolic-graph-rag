# Task 1A — Enrichment, Schema, and Prefect Orchestration

## What You Build

This stage turns the raw graph foundation into a graph that is readable and
useful for later retrieval and RAG work.

Pipeline after this stage:

KEGG -> normalize -> enrich -> load -> Neo4j
                              ^
                           Prefect

At the end of this task, the graph should contain:

- readable compound names
- richer reaction metadata
- enzyme nodes and links
- pathway nodes and links
- graph constraints
- a Prefect flow to orchestrate ingestion

## Why This Stage Matters

Task 1 proves that data can be loaded.
Task 1A makes that data usable.

Without enrichment and constraints, later API and RAG layers become harder to
debug and less informative.

## Prerequisites

- Task 1 completed
- Neo4j running locally
- `uv sync` already done

## What To Look At In The Repo

- `etl/enrich/compound_enrichment.py`
- `etl/models/`
- `graph/schema.cypher`
- `orchestration/prefect/ingestion_flow.py`
- `etl/load/neo4j_loader.py`

## Target Graph Shape

- `(:Pathway)-[:HAS_REACTION]->(:Reaction)`
- `(:Compound)-[:CONSUMED_BY]->(:Reaction)`
- `(:Reaction)-[:PRODUCES]->(:Compound)`
- `(:Reaction)-[:CATALYZED_BY]->(:Enzyme)`

## Steps

### 1. Inspect the enrichment layer

Read the enrichment and normalization code to understand how biological details
become graph-ready entities:

- compound names
- reaction names and definitions
- reaction equations and reversibility
- enzyme EC identifiers

### 2. Apply graph constraints

Inspect `graph/schema.cypher`.

The tutorial expectation is that the graph enforces uniqueness for:

- pathway IDs
- reaction IDs
- compound IDs
- enzyme EC numbers

If needed, apply the schema before running ingestion again.

### 3. Re-run ingestion and confirm the richer graph

Use the same ingestion flow from Task 1:

```bash
uv run python etl/ingest_kegg_cli.py
```

### 4. Verify enrichment in Neo4j

Run checks such as:

```cypher
MATCH (c:Compound) WHERE c.name IS NOT NULL
RETURN c.id, c.name
LIMIT 10;
```

```cypher
MATCH (r:Reaction)-[:CATALYZED_BY]->(e:Enzyme)
RETURN r.id, e.ec
LIMIT 10;
```

```cypher
MATCH (p:Pathway)-[:HAS_REACTION]->(r:Reaction)
RETURN p.id, p.name, count(r)
ORDER BY p.id;
```

### 5. Inspect the Prefect flow

Read:

- `orchestration/prefect/ingestion_flow.py`

Understand how the project moved from one-off CLI execution toward orchestrated
flows and repeatable ingestion.

### 6. Run the Prefect workflow

Use the current repository workflow:

```bash
make prefect-server
make prefect-worker
make prefect-deploy-all
```

Then trigger a deployment, for example:

```bash
uv run prefect deployment run 'kegg_batch_pathway_ingestion/local-batch' --params '{"pathway_ids":["map00010","map00020"]}'
```

## Verification

You have completed this stage when:

- compounds have readable names in Neo4j
- reactions include richer metadata
- enzyme nodes and links exist
- pathway links exist
- the Prefect flow runs successfully

## Current Repo State

This repository already contains the enriched graph model and Prefect flow.
Use this task to understand the data model and orchestration path rather than
rebuilding it from scratch.

## Historical Note

Airflow is preserved under `orchestration/airflow/` as archived project context.
It is not the recommended orchestration path for current tutorial use.

## What You Should Understand Before Moving On

- why a readable graph is more important than a merely populated graph
- why constraints matter before APIs are added
- why Prefect is the active orchestration path in the current repo

## Next Task

Continue to [Task 2](./task2.md) to expose this graph through a retrieval API.
