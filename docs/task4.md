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

## Phase 4.1 — Model Wrapper

Wrap RAG as a Giskard-compatible model.

Required interface:

def rag_predict(question: str) -> str

Optional trace interface:

def rag_predict_with_trace(question: str) -> dict

Trace includes:
- answer
- retrieved_reactions
- retrieved_compounds
- retrieved_enzymes
- context

Deliverables:
- [ ] Giskard model wrapper implemented
- [ ] RAG trace accessible to tests
- [ ] Wrapper isolated from FastAPI

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
- [ ] Rule functions implemented
- [ ] Rule functions unit tested
- [ ] Clear pass/fail output structure

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
- [ ] Giskard test suite defined
- [ ] Tests run locally
- [ ] Failures clearly reported

Implementation note:
- The repository runner keeps the `giskard.scan(...)` step optional behind
  `APP_TASK4_ENABLE_GISKARD_SCAN=1` to avoid accidental API spend during routine local runs.

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
  retrieved_reactions,
  retrieved_compounds,
  grounding_passed,
  failed_tests
}

Deliverables:
- [ ] Evaluation runner implemented
- [ ] Results stored
- [ ] Summary metrics printed

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
