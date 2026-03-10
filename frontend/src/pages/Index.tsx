import { useState } from "react";
import QueryInput from "@/components/QueryInput";
import ResponsePanel from "@/components/ResponsePanel";
import GraphViewer from "@/components/GraphViewer";
import EntityDetailPanel from "@/components/EntityDetailPanel";
import ThemeToggle from "@/components/ThemeToggle";
import ApiHealthIndicator from "@/components/ApiHealthIndicator";
import { fetchEntityById, queryRag, type EntityDetail, type RAGResponse } from "@/services/api";
import type { GraphNode, GraphEdge } from "@/services/mockApi";

interface QueryResultView {
  answer: string;
  sources: string[];
  nodes: GraphNode[];
  edges: GraphEdge[];
}

function toSourceChips(response: RAGResponse): string[] {
  const sourceIds = new Set<string>();

  response.reactions.forEach((r) => sourceIds.add(`Reaction:${r.reaction_id}`));
  response.compounds.forEach((c) => sourceIds.add(`Compound:${c.compound_id}`));
  response.enzymes.forEach((ec) => sourceIds.add(`EC:${ec}`));
  response.trace.pathway_ids.forEach((p) => sourceIds.add(`Pathway:${p}`));

  if (sourceIds.size === 0 && response.interpretation.entity_id) {
    sourceIds.add(`Entity:${response.interpretation.entity_id}`);
  }

  return Array.from(sourceIds);
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

const Index = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<QueryResultView | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [hasQueried, setHasQueried] = useState(false);

  // Entity detail panel state
  const [entityDetail, setEntityDetail] = useState<EntityDetail | null>(null);
  const [entityLoading, setEntityLoading] = useState(false);
  const [entityError, setEntityError] = useState<string | null>(null);

  const handleQuery = async (query: string) => {
    setIsLoading(true);
    setHasQueried(true);
    setEntityDetail(null);
    setEntityError(null);
    setQueryError(null);
    try {
      const response = await queryRag(query);
      setResult({
        answer: response.answer,
        sources: toSourceChips(response),
        // Step 3 will map live RAG retrieval payload into graph nodes/edges.
        nodes: [],
        edges: [],
      });
    } catch (err: unknown) {
      console.error("Query failed:", err);
      setResult(null);
      setQueryError(getErrorMessage(err, "Failed to query RAG API"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeIdClick = async (id: string) => {
    setEntityLoading(true);
    setEntityError(null);
    setEntityDetail(null);
    try {
      const detail = await fetchEntityById(id);
      setEntityDetail(detail);
    } catch (err: unknown) {
      setEntityError(getErrorMessage(err, "Failed to fetch entity details"));
    } finally {
      setEntityLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Header */}
      <header className="glass-card sticky top-0 z-50 border-b border-border/50 px-6 py-3" style={{ borderRadius: 0 }}>
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3 group">
            <div className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-primary transition-transform duration-300 group-hover:scale-110">
              <span className="text-sm font-bold text-primary-foreground">M</span>
              <div className="absolute inset-0 rounded-lg bg-primary/20 animate-glow-pulse" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-foreground tracking-tight">
                MetaGraph RAG
              </h1>
              <p className="text-[11px] text-muted-foreground">
                Metabolic Pathway Knowledge Graph
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ApiHealthIndicator />
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-4 p-6">
        {/* Query bar */}
        <div className="animate-fade-in">
          <QueryInput onSubmit={handleQuery} isLoading={isLoading} />
        </div>

        {/* Results grid */}
        <div className="grid flex-1 grid-cols-1 gap-4 lg:grid-cols-5" style={{ minHeight: "calc(100vh - 200px)" }}>
          {/* Text response */}
          <div className={`lg:col-span-2 ${hasQueried ? "animate-fade-in" : ""}`} style={hasQueried ? { animationDelay: "0.1s", opacity: 0 } : undefined}>
            <ResponsePanel
              answer={result?.answer ?? ""}
              sources={result?.sources ?? []}
              isLoading={isLoading}
              error={queryError}
            />
          </div>

          {/* Graph */}
          <div className={`lg:col-span-3 ${hasQueried ? "animate-fade-in" : ""}`} style={hasQueried ? { animationDelay: "0.2s", opacity: 0 } : undefined}>
            <GraphViewer
              nodes={result?.nodes ?? []}
              edges={result?.edges ?? []}
              onNodeClick={(label) => handleQuery(`Tell me about ${label}`)}
              onNodeIdClick={handleNodeIdClick}
              detailPanel={
                <EntityDetailPanel
                  detail={entityDetail}
                  isLoading={entityLoading}
                  error={entityError}
                  onClose={() => {
                    setEntityDetail(null);
                    setEntityError(null);
                  }}
                  onNavigate={handleNodeIdClick}
                />
              }
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
