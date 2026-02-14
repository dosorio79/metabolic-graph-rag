# Task 1A — Enrichment Pipeline & Prefect Orchestration

## Objective
Extend the ingestion pipeline with core biological entity enrichment and introduce Prefect as a lightweight orchestration layer, producing a readable and structurally correct metabolic graph in Neo4j.

This task builds directly on Task 1 and keeps Airflow as an archived orchestration option.

Resulting pipeline:

KEGG → normalize → enrich → load → Neo4j  
                        ↑  
                    Prefect flow

---

## Scope

Task 1A includes:

- Compound enrichment
- Reaction metadata enrichment
- Enzyme normalization
- Pathway node creation
- Prefect orchestration
- Explicit graph schema definition
- Repository orchestration reorganization

Not included:

- Gene mapping
- Disease mapping
- Drug mapping
- RAG layer
- Advanced reasoning queries

---

## Repository Organization Update

Create an orchestration folder and archive Airflow inside it.

Target structure:

project/
├── etl/
├── graph/
├── flows/
├── orchestration/
│   └── airflow/
│       ├── dags/
│       ├── docker-compose.yml
│       └── README.md
└── ...

Airflow remains available but is no longer the primary orchestration tool.

---

## Target Graph Structure

(:Pathway)
      │
      └── HAS_REACTION ──> (:Reaction)
                                       │
           ┌───────────────────────────┴───────────────────────────┐
           │                                                           │
     CONSUMES                                                    PRODUCES
           │                                                           │
     (:Compound)                                               (:Compound)

(:Reaction) ── CATALYZED_BY ──> (:Enzyme)

---

## Enrichment Targets

### Compound enrichment
Fetch compound metadata and attach:

Compound {
    id,
    name
}

Purpose:

- Human-readable graph
- Future RAG grounding
- Debugging usability

---

### Reaction enrichment
Extend parsed reactions with:

Reaction {
    id,
    equation,
    reversible,
    name,
    definition
}

Purpose:

- Reaction explainability
- Query readability
- Future reasoning support

---

### Enzyme normalization
Create enzyme nodes:

(:Enzyme {ec})

Relation:

(:Reaction)-[:CATALYZED_BY]->(:Enzyme)

Purpose:

- Future gene & disease linkage
- Cleaner graph semantics

---

### Pathway nodes
Create pathway nodes:

(:Pathway {id, name})

Relation:

(:Pathway)-[:HAS_REACTION]->(:Reaction)

Purpose:

- Pathway-level reasoning
- Query grouping
- Future disease mapping

---

## Graph Schema Definition

Create:

graph/schema.cypher

Define uniqueness constraints:

- Pathway id unique
- Reaction id unique
- Compound id unique
- Enzyme ec unique

Schema must be applied before ingestion.

---

## Prefect Orchestration

Create a Prefect flow executing:

ingest_pathway  
→ enrich_entities  
→ load_graph

Prefect provides:

- Flow state tracking
- Retry handling
- Logging
- Scheduling capability

Airflow remains archived and unused for new workflows.

---

## Implementation Steps

### 1. Compound enrichment module
Create:

etl/enrich/compound_enrichment.py

Responsibilities:

- collect compound IDs
- fetch KEGG compound entries
- extract compound names
- cache responses
- attach names to reactions

---

### 2. Reaction metadata extraction
Extend reaction parser to capture:

- NAME
- DEFINITION

from KEGG reaction entries.

---

### 3. Enzyme normalization in loader
Ensure enzyme nodes are created and linked via:

CATALYZED_BY

relationships.

---

### 4. Pathway nodes in loader
Ensure pathway nodes are created and linked via:

HAS_REACTION

relationships.

---

### 5. Prefect ingestion flow
Create:

flows/ingestion_flow.py

Flow runs ingestion → enrichment → loading.

---

### 6. Schema initialization
Add schema constraints via:

graph/schema.cypher

and apply before ingestion.

---

## Deliverables Checklist

### Pipeline
- [ ] Compound names enriched
- [ ] Reaction metadata stored
- [ ] Enzyme nodes normalized
- [ ] Pathway nodes created

### Graph
- [ ] Compounds readable in Neo4j
- [ ] Reaction nodes enriched
- [ ] Enzymes linked correctly
- [ ] Pathways linked correctly

### Prefect
- [ ] Flow executes ingestion pipeline
- [ ] Pipeline independent from Airflow

### Schema
- [ ] Graph constraints defined and applied

### Repository
- [ ] orchestration folder created
- [ ] airflow moved under orchestration/

---

## Validation Queries

Readable compounds:

MATCH (c:Compound)
RETURN c.id, c.name
LIMIT 10;

Reaction connectivity:

MATCH (r:Reaction)-[:CONSUMES]->(c:Compound)
RETURN r.id, c.name
LIMIT 10;

Enzyme linkage:

MATCH (e:Enzyme)<-[:CATALYZED_BY]-(r:Reaction)
RETURN e.ec, count(r)
ORDER BY count(r) DESC;

Pathway coverage:

MATCH (p:Pathway)-[:HAS_REACTION]->(r:Reaction)
RETURN p.id, count(r);

---

## Expected Effort

Estimated implementation time:

3–6 hours

Main effort is parser + loader updates.

---

## Completion Criteria

Task 1A is complete when:

- Graph nodes are readable
- Entities are normalized
- Loader is idempotent
- Flow orchestration runs successfully
- Schema constraints are active
- Airflow is archived but preserved
