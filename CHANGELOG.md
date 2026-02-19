# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

## [0.4.1] - 2026-02-19

### Fixed
- API Docker image now installs `openai`, resolving startup failure in Docker smoke tests (`ModuleNotFoundError: openai`).
- Quoted package constraints in `backend/Dockerfile` install command for safer shell parsing in CI builds.

## [0.4.0] - 2026-02-18

### Added
- Prefect batch ingestion flow (`kegg_batch_pathway_ingestion`) with per-pathway success/failure reporting.
- Make targets for batch flow execution and deployment (`flow-batch`, `prefect-deploy-batch`, `prefect-deploy-all`).
- Manual RAG validation notebook checks for expected-vs-actual classification and grounding, including failed-row debug view.
- Additional backend and ETL tests for query understanding, pathway alias resolution, and KEGG reaction-source coverage.

### Changed
- RAG query rules improved for consumer phrasing (`use`, `using`) and broader entity-name extraction patterns.
- Pathway retrieval now supports `mapXXXXX -> hsaXXXXX` alias fallback when organism-specific pathways are present.
- KEGG ingestion now unions reaction ids from module entries, pathway text, and `link/rn` endpoint to improve coverage.
- Prefect deployment commands updated to current CLI syntax and non-interactive mode.
- Task 3 and quickstart documentation updated with final validation metrics and Prefect batch workflow.

## [0.3.0] - 2026-02-16

### Added
- Task 2 retrieval API implementation and Dockerized backend workflow.
- Stronger backend quality checks: API edge-case tests, OpenAPI checks, and Docker smoke test.
- RAG runtime foundation under `backend/app/rag/` (query understanding, retrieval pipeline, context builder, LLM client, `/rag/query` endpoint).

### Changed
- Test workflow hardening and CI alignment with archived Airflow split.
- Prefect flow/schema/reset improvements and ETL reliability updates.

## [0.2.0] - 2026-02-14

### Added
- Airflow DAG, compose setup, and related tests for ingestion orchestration.

### Changed
- Documentation updates and version bump to `0.2.0`.

## [0.1.1] - 2026-02-11

### Changed
- Repository hygiene updates: stop tracking `.env` and ignore runtime artifacts.

[Unreleased]: https://github.com/dosorio79/metabolic-graph-rag/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/dosorio79/metabolic-graph-rag/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/dosorio79/metabolic-graph-rag/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/dosorio79/metabolic-graph-rag/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/dosorio79/metabolic-graph-rag/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/dosorio79/metabolic-graph-rag/releases/tag/v0.1.1
