# Task 2 — Graph Retrieval API (FastAPI + Neo4j)

## Objective
Expose metabolic graph data through a clean retrieval API.

This stage does NOT include LLM or RAG yet.
Goal is to reliably query Neo4j and serve results via FastAPI.

Architecture:
Neo4j → FastAPI → retrieval endpoints → Frontend

This enables:
- testing graph correctness
- validating schema design
- preparing retrieval for later RAG integration

---

## Scope
In this task we will:
1) Add FastAPI backend
2) Connect backend to Neo4j
3) Implement graph retrieval endpoints
4) Validate retrieval queries
5) Optionally connect existing Lovable frontend template
6) Prepare retrieval layer for RAG stage

Not included:
- embeddings
- LLM integration
- RAG ranking
- disease/drug/gene enrichment

---

## Folder Structure Target
backend/
  app/
    main.py
    config.py
    db/
      neo4j.py
    api/
      routes/
        health.py
        compounds.py
        reactions.py
        pathways.py
    services/
      graph_queries.py
    schemas/
      graph.py
  pyproject.toml  (uv)  OR requirements.txt

---

## API Functional Goals

### Health check
Endpoint:
GET /health

Returns:
- API status
- Neo4j connectivity

Deliverable:
- [x] /health returns 200 and includes API + Neo4j status fields

---

### Compound lookup
Endpoint:
GET /compounds/{compound_id}

Example:
GET /compounds/C00036

Returns:
- compound id, name
- reactions that CONSUME it
- reactions that PRODUCE it

Deliverables:
- [x] compound exists returns 200 with structured payload
- [x] compound missing returns 404 with clear message
- [x] payload includes both consuming and producing reaction lists

---

### Reaction lookup
Endpoint:
GET /reactions/{reaction_id}

Example:
GET /reactions/R00209

Returns:
- reaction id, name, definition, reversible, equation
- substrates: list of {id, name, coef}
- products: list of {id, name, coef}
- enzymes: list of EC numbers

Deliverables:
- [x] reaction exists returns 200 with structured payload
- [x] reaction missing returns 404
- [x] coefficients are present and numeric

---

### Pathway lookup
Endpoint:
GET /pathways/{pathway_id}

Example:
GET /pathways/hsa00010

Returns:
- pathway id, name
- reactions in pathway (id + optional name)
- summary counts (reactions, compounds, enzymes)

Deliverables:
- [x] pathway exists returns 200
- [x] pathway missing returns 404
- [x] payload includes reaction list ordered deterministically (by reaction id)
- [x] payload includes `reaction_count`, `compound_count`, and `enzyme_count`

---

## Neo4j Query Layer Rule
All Cypher queries must live only in:
backend/app/services/graph_queries.py

No Cypher in route handlers.

Deliverables:
- [x] routes call service functions only
- [x] service functions return Python dicts consumed by typed schemas

---

## Pydantic Schemas
Define response models in:
backend/app/schemas/graph.py

Deliverables:
- [x] CompoundResponse schema
- [x] ReactionResponse schema
- [x] PathwayResponse schema
- [x] consistent naming and field types across endpoints

---

## Testing & Validation

### Swagger UI check
Deliverables:
- [x] OpenAPI docs available at /docs
- [x] each endpoint has documented responses and path params

### Graph correctness via API
Run minimal checks (examples):
- [x] /compounds/C00036 returns a name
- [x] /reactions/R00014 returns substrates and products
- [x] /pathways/hsa00010 returns 1+ reactions

---

## Optional: Frontend Integration (Lovable template)
If useful, wire the template to the API.

Deliverables:
- [ ] set API base URL via env (e.g., VITE_API_URL)
- [ ] one page can search a compound id and render returned JSON nicely
- [ ] basic error states (404, network error)

---

## Success Criteria
Task 2 is complete when:
- [x] FastAPI connects to Neo4j reliably
- [x] compound, reaction, pathway retrieval endpoints work end-to-end
- [x] queries are isolated in services layer
- [x] schemas are defined and responses are consistent
- [x] basic manual checks against a populated local graph pass
- [ ] optional: Lovable frontend can call at least one endpoint

---

## Notes for Task 3 (next)
Task 3 will add RAG capabilities:
- embeddings for nodes/paths
- hybrid retrieval (Cypher + vector)
- LLM reasoning over retrieved subgraphs
- tool-driven “explain this pathway / disease link” flows
