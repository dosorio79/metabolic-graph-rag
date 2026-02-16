///////////////////////////////////////////////////////////////
// METABOLIC GRAPH — SANITY DASHBOARD
// Run queries individually in Neo4j Browser
///////////////////////////////////////////////////////////////


///////////////////////////////
// 1. Node counts
///////////////////////////////
MATCH (p:Pathway) RETURN "Pathways" AS entity, count(p) AS count
UNION ALL
MATCH (r:Reaction) RETURN "Reactions", count(r)
UNION ALL
MATCH (c:Compound) RETURN "Compounds", count(c)
UNION ALL
MATCH (e:Enzyme) RETURN "Enzymes", count(e);


///////////////////////////////
// 2. Compounds missing names
///////////////////////////////
MATCH (c:Compound)
WHERE c.name IS NULL
RETURN c.id
LIMIT 20;


///////////////////////////////
// 3. Reactions missing metadata
///////////////////////////////
MATCH (r:Reaction)
WHERE r.name IS NULL OR r.definition IS NULL
RETURN r.id, r.name, r.definition
LIMIT 20;


///////////////////////////////
// 4. Reactions without compounds
///////////////////////////////
MATCH (r:Reaction)
WHERE NOT (r)--(:Compound)
RETURN r.id
LIMIT 20;


///////////////////////////////
// 5. Reactions without enzymes
///////////////////////////////
MATCH (r:Reaction)
WHERE NOT (r)-[:CATALYZED_BY]->(:Enzyme)
RETURN r.id
LIMIT 20;


///////////////////////////////
// 6. Pathways without reactions
///////////////////////////////
MATCH (p:Pathway)
WHERE NOT (p)-[:HAS_REACTION]->(:Reaction)
RETURN p.id
LIMIT 20;


///////////////////////////////
// 7. Top metabolic hub compounds
///////////////////////////////
MATCH (c:Compound)
RETURN c.name, size((c)--()) AS degree
ORDER BY degree DESC
LIMIT 10;


///////////////////////////////
// 8. Reaction connectivity
///////////////////////////////
MATCH (r:Reaction)
RETURN r.id,
       size((r)--()) AS degree
ORDER BY degree ASC
LIMIT 10;


///////////////////////////////
// 9. Orphan compounds
///////////////////////////////
MATCH (c:Compound)
WHERE NOT (c)--()
RETURN c.id, c.name
LIMIT 20;


///////////////////////////////
// 10. Sample pathway visualization
///////////////////////////////
MATCH (p:Pathway)-[:HAS_REACTION]->(r:Reaction)
OPTIONAL MATCH (r)-[:PRODUCES]->(c:Compound)
RETURN p, r, c
LIMIT 50;
