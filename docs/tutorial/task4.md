# Task 4 — Grounding Evaluation and Regression Testing

## What You Build

This stage adds evaluation around the RAG system.

Pipeline after this stage:

Retrieval -> Context -> LLM -> Answer -> Grounding checks

At the end of this task, you can:

- run deterministic grounding validation
- record evaluation results
- track prompt changes with version markers
- optionally run Giskard-assisted workflows

## Why This Stage Matters

Without evaluation, RAG quality discussions stay anecdotal.

This stage makes the project testable at the answer level, not only at the API
or retrieval level.

## Prerequisites

- Task 3 completed
- `/rag/query` working
- prompt versions tracked in `backend/app/rag/prompt_registry.py`

## What To Look At In The Repo

- `evaluation/dataset/questions.json`
- `evaluation/validators/grounding_rules.py`
- `evaluation/giskard/model_wrapper.py`
- `evaluation/giskard/test_suite.py`
- `evaluation/giskard/run_evaluation.py`
- `evaluation/results/latest_results.json`

## Steps

### 1. Inspect the evaluation dataset

Read:

- `evaluation/dataset/questions.json`

Understand what kinds of questions are used for regression checks.

### 2. Inspect the deterministic grounding rules

Read:

- `evaluation/validators/grounding_rules.py`

Focus on questions like:

- does the answer cite only retrieved reactions?
- does the answer mention compounds that were actually retrieved?
- does an empty retrieval produce an insufficient-context answer?

### 3. Inspect the model wrapper

Read:

- `evaluation/giskard/model_wrapper.py`

The important idea is that evaluation wraps the RAG system without going through
FastAPI.

### 4. Run deterministic evaluation

```bash
make run-evaluation-deterministic
```

This writes:

- `evaluation/results/latest_results.json`

### 5. Inspect prompt version traceability

Read:

- `backend/app/rag/prompt_registry.py`
- `evaluation/results/latest_results.json`

Make sure you understand how prompt versions are captured so answer-quality
changes can be compared across revisions.

### 6. Optional: inspect Giskard UI workflow

If you want the richer evaluation path, review:

- `make giskard-ui-start`
- `make giskard-worker-start`
- `make giskard-publish-task4`

This is optional for the tutorial. The deterministic path is the core lesson.

## Verification

You have completed this stage when:

- the evaluation runner succeeds
- `evaluation/results/latest_results.json` is generated
- grounding failures are understandable from the output
- prompt versions are recorded with results

## Current Repo State

The repository already includes deterministic grounding checks and optional
Giskard integration. Use this task to learn how evaluation wraps the RAG stack
and makes prompt/retrieval changes measurable.

## What You Should Understand Before Moving On

- why answer-level evaluation is separate from retrieval tests
- why prompt versioning matters for regression tracking
- why deterministic grounding rules are useful even when a model is involved

## Next Task

Continue to [Task 5](./task5.md) to connect the frontend to the live retrieval
and RAG system.
