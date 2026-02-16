# Task 3 — Graph RAG Retriever Design

## Objective

Design and implement a Retrieval-Augmented Generation (RAG) layer on top of the metabolic graph.

This stage introduces:

User question → graph retrieval → context construction → LLM answer

The system remains intentionally simple:
- no agent loops yet,
- no tool orchestration,
- no autonomous reasoning.

Goal: reliable graph-grounded answers.

---

## Architecture After Task 3

User Query  
↓  
FastAPI  
↓  
Retriever Layer  
↓  
Neo4j Graph  
↓  
Context Builder  
↓  
LLM  
↓  
Answer  

This becomes the foundation for later agentic extensions.

---

## Scope of Task 3

We add:

1. Query understanding layer
2. Graph retriever
3. Context builder
4. LLM answering
5. Retrieval API endpoint

We do NOT yet add:

- multi-step agents
- tool orchestration
- planning loops
- workflow orchestration

---

## Target Folder Structure

backend/app/

- rag/
  - retriever.py
  - context_builder.py
  - llm_client.py
  - pipeline.py

- services/
  - graph_queries.py

- api/routes/
  - rag.py

---

## Step 1 — Query Understanding

Initial implementation should be rule-based.

Example questions:

- How is pyruvate produced?
- What reactions consume oxaloacetate?
- Which enzymes act on glucose?

We classify:

- compound-centric questions
- reaction-centric questions
- pathway-centric questions

Example internal representation:

{
  "entity_type": "compound",
  "entity_id": "C00022",
  "intent": "producers"
}

LLM parsing can be added later.

---

## Step 2 — Graph Retriever

Retriever maps intent to Neo4j queries.

Examples:

Compound producers:

(c:Compound)<-[:PRODUCES]-(r:Reaction)

Compound consumers:

(c:Compound)-[:CONSUMED_BY]->(r:Reaction)

Pathway expansion:

(p:Pathway)-[:HAS_REACTION]->(r)

Retriever output remains structured:

{
  reactions: [...],
  compounds: [...],
  enzymes: [...]
}

No text formatting here.

---

## Step 3 — Context Builder

Convert retrieved graph data into LLM-friendly context.

Example:

Compound: Pyruvate

Produced by:
- Reaction R00209 ...
  Enzymes: EC 1.2.1.104

Rules:

- Keep context concise
- Avoid graph dumping
- Limit reaction expansion
- Focus on relevant compounds

Goal: minimal but informative context.

---

## Step 4 — LLM Integration

Add a thin LLM client wrapper.

Possible providers:

- local Ollama
- OpenAI
- other hosted models

LLM input structure:

System: You are a metabolic pathway assistant.  
Context: ...  
Question: ...

Output is natural language grounded in graph data.

---

## Step 5 — Retrieval Endpoint

Expose retrieval via API:

POST /rag/query

Example request:

{
  "question": "How is pyruvate produced?"
}

Example response:

{
  "answer": "...",
  "reactions": [...],
  "compounds": [...]
}

This allows frontend integration later.

---

## Deliverables Checklist

### Retriever
- [ ] Intent classification logic
- [ ] Entity extraction
- [ ] Intent-to-query mapping

### Graph Retrieval
- [ ] Compound retrieval implemented
- [ ] Reaction retrieval implemented
- [ ] Pathway retrieval implemented

### Context Builder
- [ ] Context summarization logic
- [ ] Reaction listing formatting
- [ ] Enzyme inclusion

### LLM Integration
- [ ] LLM client wrapper
- [ ] Prompt template defined
- [ ] Context injection working

### API
- [ ] /rag/query endpoint implemented
- [ ] Structured response schema

### Testing
- [ ] Manual question validation
- [ ] Graph grounding verified

---

## Success Criteria

System answers:

- compound production questions
- reaction participation questions
- enzyme participation questions

Answers must be traceable to graph data.

---

## Next Stage Preview

Task 4 will introduce:

- agent planning
- tool selection
- multi-step reasoning
- disease & pathway reasoning
- multi-hop graph traversal
