# Task 6 — Answer Quality and Grounding Refinement

## What You Build

This stage improves the quality of answers produced by the live RAG stack after
frontend integration is already working.

Pipeline after this stage:

Question -> retrieval -> context builder -> prompt -> model answer -> grounding checks

At the end of this task, you can:

- tighten prompt rules for grounded answers
- require direct citation of retrieved reaction IDs
- expose pathway names from graph context
- keep the answer layer aligned with a user-visible evidence and graph exploration experience
- measure whether answer changes are real improvements instead of style drift

## Why This Stage Matters

Once Task 5 is complete, the main risk is no longer broken plumbing. The risk
is plausible but weak answers.

This stage is where the system becomes stricter about:

- when it is allowed to say "Insufficient context"
- how it cites retrieved evidence
- whether pathway names are grounded in graph data
- whether prompt changes improve or degrade answer quality

## Prerequisites

- Task 5 completed
- live `/rag/query` working
- Task 4 evaluation flow understood

## What To Look At In The Repo

- `backend/app/rag/prompt_registry.py`
- `backend/app/rag/context_builder.py`
- `backend/app/rag/retriever.py`
- `backend/app/services/graph_queries.py`
- `tests/backend/test_llm_client.py`
- `tests/backend/test_rag_retriever.py`
- `tests/backend/test_context_builder.py`

## Steps

### 1. Inspect the active prompt rules

Read:

- `backend/app/rag/prompt_registry.py`

Focus on rules such as:

- do not speculate beyond context
- cite reaction IDs when reactions are present
- do not use vague uncertainty unless the context itself is uncertain
- only mention pathway names when they appear in retrieved graph context

### 2. Inspect how context is assembled

Read:

- `backend/app/rag/context_builder.py`
- `backend/app/rag/retriever.py`

Understand how the context now includes:

- retrieved reactions
- compounds
- enzymes
- pathway identifiers and names
- trace metadata used for grounding

### 3. Inspect pathway extraction from the graph layer

Read:

- `backend/app/services/graph_queries.py`

The key idea is that pathway labels such as glycolysis or the TCA cycle should
come from the graph, not from model memory.

### 4. Run targeted backend tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest \
  tests/backend/test_rag_retriever.py \
  tests/backend/test_context_builder.py \
  tests/backend/test_llm_client.py -q
```

These tests protect the grounding contract while prompt and retrieval behavior
continue to evolve.

### 5. Verify one live example

With the stack running, submit a question such as:

- `How is pyruvate produced?`

Confirm:

- the answer cites reaction IDs directly
- pathway names are only used when they are present in retrieved context
- the answer does not fall back to `Insufficient context` when relevant reactions are already listed

## Verification

You have completed this stage when:

- prompt rules explicitly enforce grounded answer behavior
- context includes pathway names when graph data supports them
- targeted backend tests pass
- live answers cite retrieved evidence more directly than before

## Current Repo State

This work has already started in the current repository:

- prompt templates are at `system.v2` and `user.v2`
- reaction ID citation is required when reactions are present
- pathway names are extracted from retrieved graph context
- tests already cover prompt behavior, retriever output, and context rendering

Use this task to understand the current answer-quality refinement layer and to
continue iterating on it intentionally.

## What You Should Understand After This Stage

- why prompt quality problems are different from retrieval failures
- why pathway names need graph evidence instead of model inference
- why answer text should support the graph exploration flow instead of competing with it
- how to turn vague answer complaints into concrete prompt or context rules

## Next Task

There is no required Task 7 yet. Natural next topics are:

- richer answer formatting and citation rendering in the UI
- better graph summarization and interaction for large retrieval sets
- agentic workflows built on top of the grounded RAG baseline
