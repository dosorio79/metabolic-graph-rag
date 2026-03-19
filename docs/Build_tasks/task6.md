# Task 6 — Answer Quality and Grounding Refinement

## Objective

Improve the quality of live RAG answers after the end-to-end stack is already
working.

This task focuses on the answer layer itself:

Question -> Retrieval -> Context -> Prompt -> Model Answer -> Grounding Checks

The goal is to make answers more auditable, more specific, and less likely to
hide behind vague language when the graph already contains usable evidence.

---

## Why Task 6 Is Needed

By the end of Task 5, the system can already answer through the full stack:

- frontend query submission works
- backend `/rag/query` is live
- Neo4j-backed retrieval returns compounds, reactions, and pathways
- the UI renders results and graph state

At that point, the main problem is no longer missing plumbing. The main problem
is answer discipline.

Observed failure modes for this stage:

- the model says `Insufficient context` even when retrieved reactions are present
- the answer is grounded loosely instead of citing visible evidence
- pathway names are implied from model priors instead of explicit graph context
- vague wording such as `may contribute` weakens otherwise usable answers
- answer text and UI evidence presentation can drift apart, leaving the user with IDs that are technically correct but not very usable

Task 6 exists to reduce those failure modes before adding any agentic layer.

---

## Scope

### In scope

1. Tighten the RAG prompt contract.
2. Require explicit reaction ID citation when reactions are present.
3. Derive pathway names from retrieved graph context instead of model memory.
4. Extend tests around prompt behavior, retriever output, and context assembly.
5. Keep answer/citation behavior compatible with a visible graph exploration workflow in the frontend.
6. Verify live answer quality against a real running stack.

### Out of scope

- multi-step agent loops
- tool selection frameworks
- planner/executor architectures
- autonomous decomposition of metabolic questions

---

## Architecture Target After Task 6

Question
-> Retrieval
-> Context builder
-> Prompt templates
-> Model answer
-> Deterministic grounding validation

The output should be:

- more specific
- more evidence-citing
- more pathway-aware
- better aligned with a frontend where users can inspect evidence and explore the graph directly
- easier to evaluate across prompt revisions

---

## Implementation Plan

## Phase 6.1 — Prompt Contract Tightening

Refine `backend/app/rag/prompt_registry.py`.

Deliverables:
- [x] Forbid vague uncertainty unless the context is explicitly uncertain.
- [x] Require direct reaction ID citation when reactions are present.
- [x] Reserve `Insufficient context` for cases where relevant entities or reactions are actually absent.
- [x] Bump prompt version markers to preserve regression traceability.

---

## Phase 6.2 — Context and Pathway Enrichment

Improve retrieval/context assembly so pathway labels can be grounded in graph
data rather than inferred by the model.

Deliverables:
- [x] Extract pathway IDs and names from reaction membership.
- [x] Surface pathway names in the rendered RAG context.
- [x] Keep pathway usage in answers tied to retrieved evidence.

Likely touch points:
- `backend/app/rag/retriever.py`
- `backend/app/rag/context_builder.py`
- `backend/app/services/graph_queries.py`
- `backend/app/schemas/rag.py`

---

## Phase 6.3 — Test Coverage

Add or update tests so prompt and context changes are protected.

Deliverables:
- [x] Prompt/LLM client tests updated.
- [x] Retriever tests updated for pathway extraction.
- [x] Context builder tests updated for pathway rendering.

Suggested test targets:
- `tests/backend/test_llm_client.py`
- `tests/backend/test_rag_retriever.py`
- `tests/backend/test_context_builder.py`

---

## Phase 6.4 — Live Verification

Verify behavior against the running API and Neo4j instances.

Deliverables:
- [x] Real `/rag/query` checked after container refresh.
- [x] Verified that live answers now use retrieved reactions instead of defaulting to refusal.
- [x] Confirmed container env wiring so the live model path uses `APP_LLM_API_KEY`.

Representative question:
- `How is pyruvate produced?`

Expected behavior:
- cite representative reaction IDs
- use pathway names only when present in retrieved context
- avoid vague uncertainty wording

---

## Success Criteria

Task 6 is complete when:

- prompt rules clearly define grounded answer behavior
- the model cites retrieved reaction IDs in relevant answers
- pathway names come from graph-backed context
- prompt/context changes are protected by targeted backend tests
- live answers improve without introducing unsupported claims

---

## Risks and Guardrails

- Stronger prompts can become brittle:
  - Guardrail: keep tests around answer contract behavior.
- Pathway enrichment can over-expand context:
  - Guardrail: keep context size bounded and pathway summaries concise.
- Improved wording can still hide unsupported claims:
  - Guardrail: prefer explicit citation requirements over stylistic guidance alone.

---

## System State After Task 6

Graph RAG becomes:

- better grounded
- more auditable
- more stable under prompt iteration

This prepares the system for:

Task 7 — Agentic Graph Reasoning
