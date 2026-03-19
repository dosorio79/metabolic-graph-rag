# Tutorial Path

This folder is the guided learning path for the project.

The goal is to help a reader understand the system in a clean order, verify
each layer locally, and see how the repository grows from data ingestion to
graph retrieval, RAG, evaluation, and frontend integration.

## Recommended Order

1. [Task 1](./task1.md)
   Graph foundation: run Neo4j, understand the ETL shape, and load the first
   KEGG-derived graph data manually.
2. [Task 1A](./task1a.md)
   Enrichment and orchestration: add readable biological entities, graph
   constraints, and Prefect-based orchestration.
3. [Task 2](./task2.md)
   Retrieval API: expose compounds, reactions, pathways, and health checks
   through FastAPI.
4. [Task 3](./task3.md)
   Graph RAG: classify questions, retrieve graph context, build prompts, and
   answer through `/rag/query`.
5. [Task 4](./task4.md)
   Evaluation: validate grounding and track prompt/regression quality with
   deterministic rules and Giskard tooling.
6. [Task 5](./task5.md)
   Frontend integration: connect the React app to the live backend and use the
   UI as a practical regression surface.
7. [Task 6](./task6.md)
   Answer quality refinement: tighten grounding rules, pathway-aware context,
   and prompt behavior after the full stack is connected.

## How To Use These Docs

- Treat each task as a learning stage, not a verbatim changelog.
- Follow the `Prerequisites`, `Steps`, and `Verification` sections in order.
- Use the main [README](../../README.md), [quickstart](../quickstart.md), and
  [development guide](../development.md) for current run commands.
- When a task mentions an archived path, it is background only, not the
  recommended default workflow.

## Current Project Shape

The repository already contains all stages in working form. These task docs are
best used to understand:

- why each layer exists
- what files own each responsibility
- how to verify that layer locally
- what the next stage adds on top

## Notes

- Airflow is kept as archived/original orchestration context.
- Prefect is the primary orchestration path in the current repository.
- Current local examples use `map...` pathways such as `map00010`, which match
  the sample dataset and current quickstart flow.
