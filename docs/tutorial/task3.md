# Task 3 — Graph RAG on Top of Retrieval

## What You Build

This stage turns the retrieval API into a graph-grounded answering system:

User question -> query understanding -> graph retrieval -> context builder -> LLM answer

At the end of this task, the backend can answer natural-language questions
through:

- `POST /rag/query`

## Why This Stage Matters

This is the first stage where the system stops returning raw graph data and
starts synthesizing answers.

The important discipline here is that the LLM does not replace retrieval. It
sits on top of retrieval and must stay grounded in graph evidence.

## Prerequisites

- Task 2 completed
- retrieval endpoints working
- graph populated with pathways, reactions, compounds, and enzymes

## What To Look At In The Repo

- `backend/app/rag/query_understanding.py`
- `backend/app/rag/retriever.py`
- `backend/app/rag/context_builder.py`
- `backend/app/rag/llm_client.py`
- `backend/app/rag/pipeline.py`
- `backend/app/api/routes/rag.py`

## Steps

### 1. Inspect question understanding

Read the rule-based classifier and understand how a question is mapped to:

- `entity_type`
- `entity_id` or `entity_name`
- `intent`

Use examples such as:

- `How is pyruvate produced?`
- `What reactions consume oxaloacetate?`
- `Which enzymes act on glucose?`

### 2. Inspect the graph retriever

Read `backend/app/rag/retriever.py`.

The main idea is:

- use the interpreted entity and intent
- call graph query helpers
- return structured retrieval data, not prose

### 3. Inspect the context builder

Read `backend/app/rag/context_builder.py`.

Focus on:

- bounded context size
- reaction and compound formatting
- how trace IDs are exposed for grounding

### 4. Inspect the LLM wrapper and prompts

Read:

- `backend/app/rag/llm_client.py`
- `backend/app/rag/prompt_registry.py`

Understand:

- how fallback behavior works when no API key is configured
- how prompt versions are tracked
- why grounded prompting matters more than “smart” free-form generation

### 5. Verify the RAG endpoint

Run:

```bash
curl -X POST http://localhost:8000/rag/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"How is pyruvate produced?"}'
```

Inspect the response:

- `answer`
- `interpretation`
- `context`
- `reactions`
- `compounds`
- `trace`

## Verification

You have completed this stage when:

- `/rag/query` returns a structured response
- the answer can be traced back to reaction/compound/pathway evidence
- fallback behavior is deterministic when the LLM is unavailable

## Current Repo State

The repository already includes a working RAG path, prompt registry, and
grounding-aware response structure. Use this task to understand and verify the
pipeline end to end.

## What You Should Understand Before Moving On

- why query understanding is separate from retrieval
- why retrieval output should stay structured
- why context size and prompt shape strongly affect answer quality
- why traceability matters before evaluation tooling is added

## Next Task

Continue to [Task 4](./task4.md) to evaluate answer grounding and regression
quality.
