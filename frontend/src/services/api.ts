// Metabolic Graph Retrieval API client
// Matches the OpenAPI 3.0.3 contract

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/* ── Shared types ── */

export interface ServiceStatus {
  status: string;
  detail?: string | null;
}

export interface HealthResponse {
  api_status: ServiceStatus;
  neo4j_status: ServiceStatus;
}

export interface ErrorResponse {
  detail: string;
}

/* ── RAG ── */

export type RAGEntityType = "compound" | "reaction" | "pathway" | "enzyme" | "unknown";
export type RAGIntent = "producers" | "consumers" | "participants" | "summary" | "unknown";

export interface RAGInterpretation {
  entity_type: RAGEntityType;
  entity_id?: string | null;
  entity_name?: string | null;
  intent: RAGIntent;
  confidence: number;
}

export interface RAGTrace {
  reaction_ids: string[];
  compound_ids: string[];
  pathway_ids: string[];
  enzyme_ecs: string[];
}

export interface RAGCompoundSummary {
  compound_id: string;
  name?: string | null;
}

export interface RAGPathwaySummary {
  pathway_id: string;
  name?: string | null;
}

export interface RAGEvidence {
  reactions: ReactionSummary[];
  compounds: RAGCompoundSummary[];
  pathways: RAGPathwaySummary[];
  enzymes: string[];
}

export interface RAGResponse {
  answer: string;
  interpretation: RAGInterpretation;
  context?: string | null;
  reactions: ReactionSummary[];
  compounds: RAGCompoundSummary[];
  enzymes: string[];
  evidence: RAGEvidence;
  trace: RAGTrace;
}

/* ── Compounds ── */

export interface ReactionSummary {
  reaction_id: string;
  name?: string | null;
}

export interface CompoundResponse {
  compound_id: string;
  name?: string | null;
  consuming_reactions: ReactionSummary[];
  producing_reactions: ReactionSummary[];
}

/* ── Reactions ── */

export interface CompoundAmountSummary {
  compound_id: string;
  name?: string | null;
  coef: number;
}

export interface ReactionResponse {
  reaction_id: string;
  name?: string | null;
  definition?: string | null;
  equation?: string | null;
  reversible: boolean;
  substrates: CompoundAmountSummary[];
  products: CompoundAmountSummary[];
  enzymes: string[];
}

/* ── Pathways ── */

export interface PathwayResponse {
  pathway_id: string;
  name?: string | null;
  reactions: ReactionSummary[];
  reaction_count: number;
  compound_count: number;
  enzyme_count: number;
}

/* ── Union for detail panel ── */

export type EntityType = "compound" | "reaction" | "pathway";

export type EntityDetail =
  | { type: "compound"; data: CompoundResponse }
  | { type: "reaction"; data: ReactionResponse }
  | { type: "pathway"; data: PathwayResponse };

/* ── Fetch helpers ── */

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init);
  if (!res.ok) {
    const err: ErrorResponse = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail);
  }
  return res.json();
}

export function fetchHealth(): Promise<HealthResponse> {
  return apiFetch("/health");
}

export function fetchCompound(id: string): Promise<CompoundResponse> {
  return apiFetch(`/compounds/${encodeURIComponent(id)}`);
}

export function fetchReaction(id: string): Promise<ReactionResponse> {
  return apiFetch(`/reactions/${encodeURIComponent(id)}`);
}

export function fetchPathway(id: string): Promise<PathwayResponse> {
  return apiFetch(`/pathways/${encodeURIComponent(id)}`);
}

export function queryRag(question: string): Promise<RAGResponse> {
  return apiFetch("/rag/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

/**
 * Try to guess entity type from an ID string and fetch details.
 * Conventions: C##### → compound, R##### → reaction, *pathway-like* → pathway
 */
export async function fetchEntityById(id: string): Promise<EntityDetail> {
  const upper = id.toUpperCase().trim();

  if (upper.startsWith("C") && /^C\d+$/.test(upper)) {
    return { type: "compound", data: await fetchCompound(upper) };
  }
  if (upper.startsWith("R") && /^R\d+$/.test(upper)) {
    return { type: "reaction", data: await fetchReaction(upper) };
  }
  // Assume pathway for anything else (e.g. hsa00010)
  return { type: "pathway", data: await fetchPathway(id.trim()) };
}
