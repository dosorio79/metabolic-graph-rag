# Task 6 — Evaluation-Driven Grounding and Retrieval Alignment

## Objective

Improve the quality of live RAG answers after the end-to-end stack is already
working by making failures reproducible, then fixing the highest-value backend
issues exposed by those evaluations.

This task focuses on the full answer path:

Question -> Retrieval -> Context -> Prompt -> Model Answer -> Grounding Checks

The goal is to make answers more auditable, more specific, and less likely to
hide behind vague language when the graph already contains usable evidence.
The immediate priority is not more prompt wording. The immediate priority is to
systematically detect when retrieval, entity resolution, answer generation, and
UI evidence presentation drift apart.

---

## Why Task 6 Is Needed

By the end of Task 5, the system can already answer through the full stack:

- frontend query submission works
- backend `/rag/query` is live
- Neo4j-backed retrieval returns compounds, reactions, and pathways
- the UI renders results and graph state

At that point, the main problem is no longer missing plumbing. The main problem
is answer discipline and backend alignment.

Observed failure modes for this stage:

- the model says `Insufficient context` even when retrieved reactions are present
- producer/consumer questions can surface the wrong reaction direction
- the answer is grounded loosely instead of citing visible evidence
- pathway names are implied from model priors instead of explicit graph context
- vague wording such as `may contribute` weakens otherwise usable answers
- answer text and UI evidence presentation can drift apart, leaving the user with IDs that are technically correct but not very usable
- natural-language compound lookup can fail even when the equivalent KEGG ID resolves correctly

Task 6 exists to reduce those failure modes before adding any agentic layer.

---

## Scope

### In scope

1. Build a regression-oriented evaluation loop for Task 6 failures.
2. Fix retrieval correctness for producer/consumer and related intent-sensitive questions.
3. Improve entity resolution for natural-language compound lookup.
4. Require explicit reaction ID citation when reactions are present.
5. Derive pathway names from retrieved graph context instead of model memory.
6. Add deterministic grounding checks around answer behavior and evaluation outputs.
7. Keep answer/citation behavior compatible with a visible graph exploration workflow in the frontend.
8. Verify live answer quality against a real running stack.

### Out of scope

- multi-step agent loops
- tool selection frameworks
- planner/executor architectures
- autonomous decomposition of metabolic questions

---

## Architecture Target After Task 6

Question
-> Query understanding / entity resolution
-> Retrieval
-> Context builder
-> Prompt templates
-> Model answer
-> Deterministic grounding validation
-> Frontend evidence presentation aligned with backend truth

The output should be:

- easier to evaluate across prompt and retrieval revisions
- more specific
- more evidence-citing
- more pathway-aware
- more robust to natural-language naming variation
- better aligned with a frontend where users can inspect evidence and explore the graph directly

---

## Implementation Plan

## Phase 6.1 — Regression Dataset and Evaluation Harness

Expand the existing deterministic and Giskard-backed evaluation flow so Task 6
issues are captured systematically before fixes are judged complete.

Deliverables:
- [ ] Create a Task 6 regression dataset focused on observed failure classes.
- [ ] Add paired name-vs-ID queries for the same entities.
- [ ] Add assertions for false `Insufficient context`, citation discipline, and non-empty retrieval when expected.
- [ ] Use deterministic validators as the primary gate and Giskard as a secondary exploration layer.

---

## Phase 6.2 — Retrieval Correctness for Intent-Sensitive Questions

Fix the highest-value backend issue: retrieval results for producer/consumer
queries must match the interpreted intent and must not surface contradictory
evidence.

Deliverables:
- [ ] Verify producer/consumer directionality against graph truth.
- [ ] Ensure retrieved evidence for a question is actually answer-supporting evidence.
- [ ] Prevent contradictory cases where the answer says `Insufficient context` while the UI presents seemingly supporting reactions.

Likely touch points:
- `backend/app/rag/retriever.py`
- `backend/app/services/graph_queries.py`
- `backend/app/schemas/rag.py`

---

## Phase 6.3 — Entity Resolution Hardening

Improve query understanding and lookup so normal compound names resolve
reliably, not only explicit KEGG IDs.

Deliverables:
- [ ] Support natural-language variants such as `acetyl-CoA`, `Acetyl-CoA`, and equivalent canonical graph names.
- [ ] Add regression cases comparing name-based and ID-based queries for the same entity.
- [ ] Keep resolution deterministic enough to avoid broad cross-entity collisions.

Likely touch points:
- `backend/app/rag/query_understanding.py`
- `backend/app/services/name_utils.py`
- `backend/app/services/graph_queries.py`

---

## Phase 6.4 — Context and Pathway Enrichment

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

## Phase 6.5 — Prompt Contract Tightening

Refine prompt behavior after retrieval and evaluation failures are better
controlled.

Deliverables:
- [x] Forbid vague uncertainty unless the context is explicitly uncertain.
- [x] Require direct reaction ID citation when reactions are present.
- [ ] Reserve `Insufficient context` for cases where relevant entities or reactions are actually absent in live behavior, not only in prompt wording.
- [x] Bump prompt version markers to preserve regression traceability.

Suggested test targets:
- `tests/backend/test_llm_client.py`
- `tests/backend/test_rag_retriever.py`
- `tests/backend/test_context_builder.py`

---

## Phase 6.6 — Deterministic Grounding Validation and Frontend Alignment

Close the gap between the target Task 6 architecture and the actual pipeline by
making answer/evidence contradictions visible and testable.

Deliverables:
- [ ] Add validation coverage for answer/evidence contradictions.
- [ ] Distinguish retrieved neighborhood from direct supporting evidence in evaluation and, if needed, in the frontend.
- [ ] Ensure the frontend evidence presentation does not overstate support for the answer.

Likely touch points:
- `backend/app/rag/pipeline.py`
- `evaluation/validators/grounding_rules.py`
- `evaluation/giskard/test_suite.py`
- `frontend/src/components/ResponsePanel.tsx`

---

## Phase 6.7 — Test Coverage

Add or update tests so retrieval, resolution, prompt, and context changes are
protected.

Deliverables:
- [ ] Prompt/LLM client tests updated for Task 6 regression cases.
- [ ] Retriever tests updated for producer/consumer correctness.
- [ ] Context builder tests updated for pathway rendering and bounded context.
- [ ] Query-understanding or lookup tests updated for name-resolution parity.

Suggested test targets:
- `tests/backend/test_llm_client.py`
- `tests/backend/test_rag_retriever.py`
- `tests/backend/test_context_builder.py`
- `tests/backend/test_query_understanding.py`
- `tests/backend/test_graph_queries.py`

---

## Phase 6.8 — Live Verification

Verify behavior against the running API and Neo4j instances.

Deliverables:
- [x] Real `/rag/query` checked after container refresh.
- [ ] Verified that live answers use retrieved reactions instead of defaulting to refusal.
- [x] Confirmed container env wiring so the live model path uses `APP_LLM_API_KEY`.
- [ ] Verified that representative compound-name queries resolve comparably to KEGG ID queries.

Representative question:
- `How is pyruvate produced?`
- `Tell me about acetyl-CoA`
- `Tell me about C00024`

Expected behavior:
- cite representative reaction IDs
- use pathway names only when present in retrieved context
- avoid vague uncertainty wording
- do not claim `Insufficient context` when relevant evidence is already retrieved
- resolve common compound names when graph content exists for the equivalent ID

---

## Success Criteria

Task 6 is complete when:

- evaluation reproduces the known failure classes and blocks regressions
- prompt rules clearly define grounded answer behavior
- producer/consumer questions return directionally correct evidence
- common compound name queries resolve when equivalent graph entities exist
- the model cites retrieved reaction IDs in relevant answers
- pathway names come from graph-backed context
- retrieval/prompt/context changes are protected by targeted backend tests
- frontend evidence presentation stays aligned with what actually supports the answer
- live answers improve without introducing unsupported claims

---

## Risks and Guardrails

- Stronger prompts can become brittle:
  - Guardrail: keep tests around answer contract behavior and avoid using prompt wording as the only enforcement layer.
- Name matching can over-broaden retrieval:
  - Guardrail: normalize aggressively but keep entity-type-specific lookup and deterministic resolution rules.
- Retrieval fixes can still leave frontend evidence misleading:
  - Guardrail: validate answer/evidence alignment explicitly.
- Pathway enrichment can over-expand context:
  - Guardrail: keep context size bounded and pathway summaries concise.
- Improved wording can still hide unsupported claims:
  - Guardrail: prefer explicit citation requirements and deterministic validation over stylistic guidance alone.

---

## System State After Task 6

Graph RAG becomes:

- evaluation-driven
- better grounded
- more auditable
- more stable under prompt iteration
- more robust to natural-language compound queries

This prepares the system for:

Task 7 — Agentic Graph Reasoning
