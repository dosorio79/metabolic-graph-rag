# Task 5 — Frontend Integration for Retrieval + RAG Testing

## Objective

Connect the existing React frontend to the live FastAPI backend so we can test
the full path:

User Query -> Frontend -> FastAPI -> Neo4j/RAG -> Frontend Visualization

This task turns the UI from a mock demo into a practical test harness for
manual QA and faster iteration.

It also establishes the graph view as a user-facing learning surface: users
should be able to see the relevant metabolic subgraph, inspect pathway context,
and explore connected entities instead of receiving only a text answer.

---

## Why Task 5 Is Needed

Current repo state shows a partial integration:

- Frontend `ApiHealthIndicator` and entity detail fetches already call real API endpoints.
- Main query flow in `frontend/src/pages/Index.tsx` still calls `queryGraphRAG` from `frontend/src/services/mockApi.ts`.
- Backend already exposes `POST /rag/query`, but frontend query response shape currently expects mock `nodes` + `edges`.
- No explicit backend CORS configuration is present for local frontend dev origin.

Result: the most important user flow is not exercising real backend retrieval/RAG behavior yet.

---

## Scope

### In scope

1. Replace mock query path with real backend RAG API calls.
2. Define and implement a graph visualization contract for RAG responses.
3. Enable browser-safe local communication (CORS or Vite proxy).
4. Add robust loading/error/empty states for integration failures.
5. Add frontend tests for API client + query flow.
6. Add one integration smoke path that validates frontend/backend wiring.
7. Preserve the graph as an explicit visible part of the product, not only as an internal support artifact.

### Out of scope

- New model providers or prompt redesign.
- Advanced agentic planning loops.
- Full production auth/session management.
- Design overhaul of the current UI.

---

## Architecture Target After Task 5

User Query
-> Frontend QueryInput
-> `POST /rag/query`
-> RAG pipeline (interpretation, retrieval, context, answer)
-> Frontend response panel + graph view + entity detail drill-down

The frontend becomes a first-class testing surface for Task 2/3/4 behavior.

---

## Implementation Plan

## Phase 5.1 — Real Query Client

Create a typed client for `POST /rag/query` in `frontend/src/services/api.ts`.

Deliverables:
- [ ] Add `RAGQueryRequest` and `RAGQueryResponse` types matching backend schemas.
- [ ] Add `queryRag(question: string)` using `BASE_URL`.
- [ ] Standardize API error parsing for `4xx/5xx` responses.

Notes:
- Preserve existing typed helpers (`fetchCompound`, `fetchReaction`, `fetchPathway`).
- Keep all API calls centralized in `frontend/src/services/api.ts`.

---

## Phase 5.2 — UI Wiring in Index Page

Replace mock usage in `frontend/src/pages/Index.tsx`.

Deliverables:
- [ ] Remove dependency on `queryGraphRAG` from `mockApi.ts` in main query path.
- [ ] Wire `handleQuery` to real `queryRag`.
- [ ] Render backend answer and usable evidence links from RAG payload.
- [ ] Add clear user-visible error state when RAG call fails.

---

## Phase 5.3 — Graph Data Contract

Frontend graph view currently needs `nodes` + `edges`, while backend RAG returns
reactions/compounds/enzymes/trace.

Choose one approach and implement end-to-end:

Option A (preferred for speed): frontend adapter
- Build deterministic `nodes`/`edges` in frontend from RAG payload.
- Use available IDs and lightweight labels; hydrate richer detail via existing
  entity panel fetches on click.

Option B: backend view model
- Add a backend response extension returning UI-ready `nodes`/`edges`.
- Keep schema versioned and documented.

Deliverables:
- [ ] Graph renders from real RAG results (no mock data dependency).
- [ ] Node click continues to open detail panel via existing entity endpoints.
- [ ] Empty retrieval cases show explicit no-context/no-results state.
- [ ] The relevant graph remains visible and explorable so users can learn from the retrieved pathway structure.

---

## Phase 5.4 — Local Connectivity (CORS / Proxy)

Enable browser calls from frontend dev server to backend.

Deliverables:
- [ ] Implement CORS middleware in FastAPI for local frontend origin(s), OR
- [ ] Configure Vite dev proxy and use relative API base in development.
- [ ] Document environment variables:
  - `VITE_API_BASE_URL` (frontend)
  - any backend CORS allowlist vars if introduced.

Acceptance:
- [ ] Browser network calls from local frontend succeed without CORS errors.

---

## Phase 5.5 — Testing

### Frontend unit/integration tests

Deliverables:
- [ ] Add tests for `queryRag` success and error handling.
- [ ] Add page-level test covering query submission -> loading -> rendered answer.
- [ ] Remove or refactor `mockApi.test.ts` to avoid false confidence from mock-only flows.

### Backend/contract checks

Deliverables:
- [ ] Confirm `/rag/query` schema stays compatible with frontend types.
- [ ] Add/update OpenAPI docs if response shape is changed for graph contract.

### Manual smoke checklist

Deliverables:
- [ ] `docker compose up -d` (Neo4j + API) and frontend dev server run together.
- [ ] Submit at least 3 representative questions (compound/reaction/pathway intent).
- [ ] Verify detail panel navigation (reaction -> compound -> reaction) works.
- [ ] Verify one failing query path (invalid/empty) shows a stable error message.

---

## Suggested File Touch List

- `frontend/src/services/api.ts`
- `frontend/src/pages/Index.tsx`
- `frontend/src/components/ResponsePanel.tsx` (if needed for error/no-results UX)
- `frontend/src/components/GraphViewer.tsx` (only if graph contract changes)
- `frontend/src/test/*` (new API/query integration tests)
- `backend/app/main.py` (if adding CORS middleware)
- `backend/app/config.py` + `.env.example` (if adding configurable CORS allowlist)
- `docs/openapi.yaml` (if backend response contract changes)
- `README.md` / `docs/quickstart.md` (run instructions for full-stack local test)

---

## Success Criteria

Task 5 is complete when:

- Frontend query flow uses real backend `/rag/query` in local development.
- Graph and answer panels render real retrieval/RAG outputs without mock data.
- Node detail drill-down works against live retrieval endpoints.
- Local frontend-backend communication works reliably (no CORS/proxy blockers).
- Automated frontend tests cover query success + failure paths.
- Team can use UI as a practical regression test surface for Task 2/3/4 outputs.
- The graph is preserved as an explicit user-facing exploration surface, not reduced to hidden supporting state.

---

## Risks and Guardrails

- Contract drift between backend RAG schema and frontend types:
  - Guardrail: keep explicit TypeScript interfaces and add contract tests.
- UI regressions from replacing mock graph payload:
  - Guardrail: introduce adapter layer and retain deterministic shape.
- Slow local feedback if full stack startup is brittle:
  - Guardrail: document one-command startup workflow where possible.

---

## Next Stage Preview

Task 6 — Answer Quality and Grounding Refinement

With frontend integration completed, the next build step is to improve answer
quality itself: tighten prompting, require explicit reaction citations, derive
pathway names from retrieved graph context, and make those changes measurable
through tests and evaluation.
