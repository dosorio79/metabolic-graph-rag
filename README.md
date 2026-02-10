# Metabolic Graph RAG

[![CI](https://github.com/dosorio79/metabolic-graph-rag/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/dosorio79/metabolic-graph-rag/actions/workflows/ci.yml)

Metabolic Graph RAG is a foundation for building a metabolic pathway knowledge graph in Neo4j, ingesting data from KEGG, and exposing graph-backed retrieval workflows for backend APIs and agent tooling.

## Goals

- Ingest pathway and reaction data from KEGG.
- Normalize and load entities into Neo4j.
- Support query-driven retrieval for RAG pipelines.
- Provide a backend-ready structure for API and agent integration.

## Project Layout

```text
metabolic-graph-rag/
├── airflow/            # DAGs and Airflow local config
├── etl/                # Fetch, normalize, and load pipeline code
├── graph/              # Neo4j client and graph query assets
├── backend/            # FastAPI application skeleton
├── rag/                # Retrieval and context assembly logic
├── agents/             # Planner and tool interfaces
├── embeddings/         # Embedding build scripts
├── data/               # Raw and normalized local artifacts
├── docs/               # Build tasks and technical documentation
└── scripts/            # Utility scripts (reset, maintenance)
```

## Tech Stack

- Python 3.12+
- `uv` for dependency and lockfile management
- Neo4j as graph database
- FastAPI + Uvicorn for backend API
- Airflow for scheduled ingestion orchestration

## Quick Start

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Set at least:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

### 3. Start Neo4j

Use your preferred method (local Docker, compose, or managed instance).  
If using Docker compose in this repo:

```bash
docker compose up -d
```

### 4. Run ingestion manually

```bash
uv run python etl/ingest_kegg.py
```

### 5. Start backend API (placeholder app)

```bash
uv run uvicorn backend.app.main:app --reload
```

## Documentation

- Project docs index: `docs/README.md`
- Task brief: `docs/Build_tasks/task1.md`
- Quickstart: `docs/quickstart.md`
- Architecture: `docs/architecture.md`
- Development workflow: `docs/development.md`

## Current Status

This repository is scaffolded for iterative implementation.  
Most modules are placeholders and should be implemented step by step from the docs build tasks.
