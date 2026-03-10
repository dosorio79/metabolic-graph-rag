// Mock FastAPI backend for metabolic pathway Graph RAG

export interface GraphNode {
  id: string;
  label: string;
  type: "metabolite" | "enzyme" | "pathway" | "reaction" | "gene";
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  relationship: string;
}

export interface QueryResponse {
  answer: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  sources: string[];
}

const MOCK_RESPONSES: Record<string, QueryResponse> = {
  glycolysis: {
    answer:
      "Glycolysis is the metabolic pathway that converts glucose (C₆H₁₂O₆) into pyruvate. The net energy yield is 2 ATP and 2 NADH per glucose molecule. It occurs in the cytoplasm and consists of 10 enzymatic steps, divided into an energy investment phase (steps 1–5) and an energy payoff phase (steps 6–10). Key regulatory enzymes include hexokinase, phosphofructokinase-1 (PFK-1), and pyruvate kinase.",
    nodes: [
      { id: "glucose", label: "Glucose", type: "metabolite" },
      { id: "g6p", label: "Glucose-6-P", type: "metabolite" },
      { id: "f6p", label: "Fructose-6-P", type: "metabolite" },
      { id: "f16bp", label: "Fructose-1,6-BP", type: "metabolite" },
      { id: "g3p", label: "G3P", type: "metabolite" },
      { id: "pyruvate", label: "Pyruvate", type: "metabolite" },
      { id: "atp", label: "ATP", type: "metabolite" },
      { id: "nadh", label: "NADH", type: "metabolite" },
      { id: "hk", label: "Hexokinase", type: "enzyme" },
      { id: "pfk1", label: "PFK-1", type: "enzyme" },
      { id: "pk", label: "Pyruvate Kinase", type: "enzyme" },
      { id: "glycolysis_pw", label: "Glycolysis", type: "pathway" },
    ],
    edges: [
      { source: "glucose", target: "g6p", label: "phosphorylation", relationship: "CONVERTS_TO" },
      { source: "g6p", target: "f6p", label: "isomerization", relationship: "CONVERTS_TO" },
      { source: "f6p", target: "f16bp", label: "phosphorylation", relationship: "CONVERTS_TO" },
      { source: "f16bp", target: "g3p", label: "cleavage", relationship: "CONVERTS_TO" },
      { source: "g3p", target: "pyruvate", label: "oxidation", relationship: "CONVERTS_TO" },
      { source: "hk", target: "glucose", label: "catalyzes", relationship: "CATALYZES" },
      { source: "pfk1", target: "f6p", label: "catalyzes", relationship: "CATALYZES" },
      { source: "pk", target: "pyruvate", label: "produces", relationship: "CATALYZES" },
      { source: "g3p", target: "nadh", label: "reduces", relationship: "PRODUCES" },
      { source: "glycolysis_pw", target: "glucose", label: "starts with", relationship: "INCLUDES" },
      { source: "glycolysis_pw", target: "pyruvate", label: "ends with", relationship: "INCLUDES" },
    ],
    sources: ["KEGG:hsa00010", "Reactome:R-HSA-70171", "MetaCyc:GLYCOLYSIS"],
  },
  default: {
    answer:
      "The citric acid cycle (TCA/Krebs cycle) is a central metabolic pathway in the mitochondrial matrix. It oxidizes acetyl-CoA to CO₂, generating 3 NADH, 1 FADH₂, and 1 GTP per turn. Key regulatory points include isocitrate dehydrogenase and α-ketoglutarate dehydrogenase, both allosterically regulated by ATP/ADP ratios and NADH/NAD⁺ levels.",
    nodes: [
      { id: "acetyl_coa", label: "Acetyl-CoA", type: "metabolite" },
      { id: "oxaloacetate", label: "Oxaloacetate", type: "metabolite" },
      { id: "citrate", label: "Citrate", type: "metabolite" },
      { id: "isocitrate", label: "Isocitrate", type: "metabolite" },
      { id: "alpha_kg", label: "α-Ketoglutarate", type: "metabolite" },
      { id: "succinate", label: "Succinate", type: "metabolite" },
      { id: "fumarate", label: "Fumarate", type: "metabolite" },
      { id: "malate", label: "Malate", type: "metabolite" },
      { id: "cs", label: "Citrate Synthase", type: "enzyme" },
      { id: "idh", label: "Isocitrate DH", type: "enzyme" },
      { id: "tca", label: "TCA Cycle", type: "pathway" },
    ],
    edges: [
      { source: "acetyl_coa", target: "citrate", label: "condensation", relationship: "CONVERTS_TO" },
      { source: "citrate", target: "isocitrate", label: "isomerization", relationship: "CONVERTS_TO" },
      { source: "isocitrate", target: "alpha_kg", label: "oxidative decarb.", relationship: "CONVERTS_TO" },
      { source: "alpha_kg", target: "succinate", label: "oxidative decarb.", relationship: "CONVERTS_TO" },
      { source: "succinate", target: "fumarate", label: "oxidation", relationship: "CONVERTS_TO" },
      { source: "fumarate", target: "malate", label: "hydration", relationship: "CONVERTS_TO" },
      { source: "malate", target: "oxaloacetate", label: "oxidation", relationship: "CONVERTS_TO" },
      { source: "oxaloacetate", target: "citrate", label: "condensation", relationship: "CONVERTS_TO" },
      { source: "cs", target: "citrate", label: "catalyzes", relationship: "CATALYZES" },
      { source: "idh", target: "isocitrate", label: "catalyzes", relationship: "CATALYZES" },
      { source: "tca", target: "acetyl_coa", label: "input", relationship: "INCLUDES" },
    ],
    sources: ["KEGG:hsa00020", "Reactome:R-HSA-71403"],
  },
};

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Mock POST /api/query
 * Simulates a FastAPI endpoint that accepts a natural language query
 * and returns a text response + Neo4j graph data.
 */
export async function queryGraphRAG(query: string): Promise<QueryResponse> {
  await delay(800 + Math.random() * 700);

  const lowerQuery = query.toLowerCase();

  if (lowerQuery.includes("glycolysis") || lowerQuery.includes("glucose")) {
    return MOCK_RESPONSES.glycolysis;
  }

  return MOCK_RESPONSES.default;
}
