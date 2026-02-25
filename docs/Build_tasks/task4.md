# Task 4 — Giskard-Based Answer Grounding Layer

## Objective

Integrate Giskard as the evaluation harness for answer-level grounding validation.

This task introduces automated, reproducible testing of LLM answers
against retrieved graph context.

Task 4 validates:

Retrieval → Context → LLM → Answer → Giskard Test Suite

This task does NOT modify retrieval logic or graph ingestion.

---

## Architecture

Graph → Retrieval → Context → LLM → Answer
                                         ↓
                              Giskard Evaluation
                                         ↓
                               Grounding Report

Giskard orchestrates tests.
Deterministic validators define grounding rules.

---

## Folder Structure

evaluation/
├── dataset/
│   └── questions.json
├── validators/
│   └── grounding_rules.py
├── giskard/
│   ├── model_wrapper.py
│   ├── test_suite.py
│   └── run_evaluation.py
└── results/
    └── latest_results.json

---

## Local Run Modes

Task 4 supports two local execution modes:

1. Deterministic grounding only (default, no Giskard LLM scan)
2. Deterministic grounding + optional Giskard LLM-assisted scan

Make targets:

- `make run-evaluation-deterministic`
- `make run-evaluation-llm`

Both read `evaluation/dataset/questions.json` and write `evaluation/results/latest_results.json`.

Prompt source/versioning:

- Active RAG prompt templates live in `backend/app/rag/prompt_registry.py`
- Prompt versions are first-class metadata (`system_prompt_version`, `user_prompt_version`)
- Task 4 stores prompt versions in each evaluated case in `evaluation/results/latest_results.json`
- Bump versions in `prompt_registry.py` when prompt wording changes to preserve regression traceability

---

## Phase 4.1 — Model Wrapper

Wrap RAG as a Giskard-compatible model.

Required interface:

def rag_predict(question: str) -> str

Optional trace interface:

def rag_predict_with_trace(question: str) -> dict

Trace includes:
- answer
- prompt_versions (`system_prompt_version`, `user_prompt_version`)
- retrieved_reactions
- retrieved_compounds
- retrieved_enzymes
- context

Deliverables:
- [x] Giskard model wrapper implemented
- [x] RAG trace accessible to tests
- [x] Wrapper isolated from FastAPI

---

## Phase 4.2 — Deterministic Grounding Rules

Implement rule functions in grounding_rules.py.

Rules:

1. Reaction Grounding
   Answer reaction IDs ⊆ retrieved_reactions

2. Compound Grounding
   Answer compound IDs ⊆ retrieved_compounds

3. Enzyme Grounding
   Answer EC numbers ⊆ retrieved_enzymes

4. Retrieval Consistency
   If retrieval non-empty → answer references at least one retrieved entity

5. Insufficient Context Behavior
   If retrieval empty → answer must explicitly state insufficient context

Deliverables:
- [x] Rule functions implemented
- [x] Rule functions unit tested
- [x] Clear pass/fail output structure

---

## Phase 4.3 — Giskard Test Suite

Use Giskard to register:

- RAG model wrapper
- Evaluation dataset
- Custom grounding tests

Each test calls deterministic rule functions.

Optional:
- Add LLM-as-judge faithfulness scoring
- Enable the LLM-assisted Giskard scan only when explicitly requested (may incur API cost)

Deliverables:
- [x] Giskard test suite defined
- [x] Tests run locally
- [x] Failures clearly reported

Implementation note:
- The repository runner keeps the `giskard.scan(...)` step optional behind
  `APP_TASK4_ENABLE_GISKARD_SCAN=1` to avoid accidental API spend during routine local runs.
- Full LLM-assisted detector coverage requires installing `giskard[llm]` (heavier dependency set).

### Local Giskard UI (Hub)

Giskard can run a local UI for interactive inspection. In this repository, the
Task 4 runner remains CLI/JSON-based, but you can start the local Hub and Worker
from Make targets:

- `make giskard-ui-start`
- `make giskard-ui-status`
- `make giskard-ui-logs`
- `make giskard-ui-stop`
- `make giskard-worker-start`
- `make giskard-worker-logs`
- `make giskard-worker-stop`

Notes:
- These commands use a repo-local Giskard home directory: `.giskard-home/`
- Analytics is disabled in the Make targets (`GSK_DISABLE_ANALYTICS=1`)
- The Hub/Worker commands typically require Docker available locally
- The Task 4 runner writes `evaluation/results/latest_results.json` for review in
  the IDE/CLI; the UI flow uses a separate publish step for dataset/model artifacts

Suggested local UI workflow:

1. Start the Hub: `make giskard-ui-start`
2. Open the UI at `http://localhost:19000`
3. Create/copy a Hub API key in the UI
4. Export the key for CLI usage: `export GSK_API_KEY=...`
5. Publish Task 4 artifacts (questions + model wrapper) to the UI project:
   `make giskard-publish-task4`
6. Start a worker (prompts for API key if `GSK_API_KEY` is not set):
   `make giskard-worker-start`

Optional environment variables for publishing:
- `GSK_HUB_URL` (default `http://localhost:19000`)
- `GSK_PROJECT_KEY` (default `metabolic-graph-rag-task4`)
- `GSK_PROJECT_NAME` (default `Metabolic Graph RAG Task 4`)

---

## Phase 4.4 — Evaluation Runner

run_evaluation.py:

- Load questions
- Execute RAG
- Run Giskard tests
- Persist results

Output structure:

{
  question,
  answer,
  system_prompt_version,
  user_prompt_version,
  retrieved_reactions,
  retrieved_compounds,
  grounding_passed,
  failed_tests
}

Deliverables:
- [x] Evaluation runner implemented
- [x] Results stored
- [x] Summary metrics printed

---

## Success Criteria

Task 4 is complete when:

- LLM answers are validated via Giskard
- Hallucinated reactions are detectable
- Hallucinated compounds are detectable
- Evaluation runs reproducibly
- Prompt changes can be regression tested

---

## System State After Task 4

Graph RAG becomes:

Answer-Grounded
Regression-Testable
LLM-Stable

This prepares the system for:

Task 5 — Agentic Graph Reasoning
