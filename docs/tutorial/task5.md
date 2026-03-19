# Task 5 — Frontend Integration and Manual QA Surface

## What You Build

This stage connects the React frontend to the live backend so the UI becomes a
real testing surface instead of a mock-only demo.

Flow after this stage:

User query -> frontend -> `/rag/query` -> backend retrieval/RAG -> UI answer + graph

At the end of this task, you can use the frontend to:

- submit real questions
- see grounded answers
- inspect the relevant graph pathways, reactions, and compounds
- verify drill-down behavior manually

## Why This Stage Matters

By this point the backend may be correct in isolation, but real product quality
depends on whether the user can exercise that behavior through the UI.

The frontend becomes the fastest place to spot:

- contract drift
- error-state problems
- missing loading states
- brittle retrieval/RAG behavior

## Prerequisites

- Task 4 completed
- backend and Neo4j running locally
- frontend dependencies installed

## What To Look At In The Repo

- `frontend/src/services/api.ts`
- `frontend/src/pages/Index.tsx`
- `frontend/src/services/graph.ts`
- `frontend/src/components/ResponsePanel.tsx`
- `frontend/src/components/GraphViewer.tsx`
- `frontend/src/test/`

## Steps

### 1. Start the backend stack

```bash
docker compose up -d
```

### 2. Start the frontend

```bash
cd frontend
npm ci
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

### 3. Inspect the real API client

Read:

- `frontend/src/services/api.ts`

Focus on:

- base URL handling
- typed request/response handling
- error parsing

### 4. Inspect the query page

Read:

- `frontend/src/pages/Index.tsx`

Understand how the page:

- submits the question
- renders loading/error states
- shows answer content
- builds graph UI state from the backend response

### 5. Verify the live query flow manually

Submit questions such as:

- `How is pyruvate produced?`
- `What reactions consume oxaloacetate?`
- `Summarize map00010`

Confirm:

- the answer panel updates
- graph content renders as a user-visible exploration surface
- clicking entities still drives detail views where expected

### 6. Inspect frontend tests

Review:

- `frontend/src/test/api.test.ts`
- `frontend/src/test/Index.test.tsx`
- `frontend/src/test/mockApi.test.ts`

The tutorial goal is to understand how the frontend protects the integration
boundary without requiring the full stack for every test.

## Verification

You have completed this stage when:

- the frontend uses the live backend query path
- answer and graph panels render real RAG output
- drill-down behavior works
- frontend tests cover API and page flow behavior

## Current Repo State

The repository has already completed most of this stage. In the current code:

- `frontend/src/services/api.ts` already calls the live backend `POST /rag/query`
- `frontend/src/pages/Index.tsx` already uses `queryRag(...)` in the main query path
- `frontend/src/services/graph.ts` already adapts RAG payloads into graph nodes and edges
- `frontend/src/components/ResponsePanel.tsx` exposes evidence links that point to KEGG entries instead of leaving IDs as inert text
- `frontend/src/components/GraphViewer.tsx` exposes the retrieved graph as something the user can inspect and play with, not just a background visualization
- `frontend/src/test/api.test.ts` and `frontend/src/test/Index.test.tsx` already cover API and page flow behavior
- `frontend/src/test/mockApi.test.ts` is now legacy coverage for fixture behavior, not the main integration path

Use this task to understand how the UI acts as a practical regression surface
for the backend, not as a greenfield implementation exercise.

## What You Should Understand After This Stage

- how backend contract decisions affect UI complexity
- how to use the frontend for manual regression testing
- why the graph view should remain a visible learning and exploration surface for the user
- where to debug when a failure is caused by retrieval, prompt behavior, or UI
  state management

## Next Task

Continue to [Task 6](./task6.md) to tighten answer quality, grounding rules,
and pathway-aware explanations now that the full stack is wired together.
