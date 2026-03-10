import type { RAGResponse, ReactionResponse } from "@/services/api";

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

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface GraphBuilderDeps {
  fetchReactionDetail: (reactionId: string) => Promise<ReactionResponse>;
}

function emptyGraph(): GraphData {
  return { nodes: [], edges: [] };
}

export async function buildGraphFromRag(
  response: RAGResponse,
  deps: GraphBuilderDeps,
): Promise<GraphData> {
  if (!response.reactions.length && !response.compounds.length) {
    return emptyGraph();
  }

  const nodes = new Map<string, GraphNode>();
  const edges = new Map<string, GraphEdge>();

  const addNode = (node: GraphNode) => {
    if (!nodes.has(node.id)) {
      nodes.set(node.id, node);
    }
  };

  const addEdge = (edge: GraphEdge) => {
    const key = `${edge.source}|${edge.target}|${edge.relationship}`;
    if (!edges.has(key)) {
      edges.set(key, edge);
    }
  };

  response.reactions.forEach((reaction) => {
    addNode({
      id: reaction.reaction_id,
      label: reaction.name || reaction.reaction_id,
      type: "reaction",
    });
  });

  const pathwayIds = new Set<string>(response.trace.pathway_ids);
  if (
    response.interpretation.entity_type === "pathway" &&
    response.interpretation.entity_id
  ) {
    pathwayIds.add(response.interpretation.entity_id);
  }
  pathwayIds.forEach((pathwayId) => {
    addNode({
      id: pathwayId,
      label: pathwayId,
      type: "pathway",
    });
  });

  const reactionIds = Array.from(new Set(response.reactions.map((reaction) => reaction.reaction_id)));

  pathwayIds.forEach((pathwayId) => {
    reactionIds.forEach((reactionId) => {
      addEdge({
        source: pathwayId,
        target: reactionId,
        label: "has reaction",
        relationship: "HAS_REACTION",
      });
    });
  });

  const reactionDetails = await Promise.allSettled(
    reactionIds.map((reactionId) => deps.fetchReactionDetail(reactionId)),
  );

  reactionDetails.forEach((result) => {
    if (result.status !== "fulfilled") {
      return;
    }
    const reaction = result.value;
    addNode({
      id: reaction.reaction_id,
      label: reaction.name || reaction.reaction_id,
      type: "reaction",
    });

    reaction.substrates.forEach((substrate) => {
      addNode({
        id: substrate.compound_id,
        label: substrate.name || substrate.compound_id,
        type: "metabolite",
      });
      addEdge({
        source: substrate.compound_id,
        target: reaction.reaction_id,
        label: `consumed${substrate.coef !== 1 ? ` (${substrate.coef})` : ""}`,
        relationship: "CONSUMED_BY",
      });
    });

    reaction.products.forEach((product) => {
      addNode({
        id: product.compound_id,
        label: product.name || product.compound_id,
        type: "metabolite",
      });
      addEdge({
        source: reaction.reaction_id,
        target: product.compound_id,
        label: `produces${product.coef !== 1 ? ` (${product.coef})` : ""}`,
        relationship: "PRODUCES",
      });
    });

    reaction.enzymes.forEach((enzymeEc) => {
      addNode({
        id: enzymeEc,
        label: enzymeEc,
        type: "enzyme",
      });
      addEdge({
        source: enzymeEc,
        target: reaction.reaction_id,
        label: "catalyzes",
        relationship: "CATALYZES",
      });
    });
  });

  // Keep focal compounds even when reaction-detail fetch is partially unavailable.
  response.compounds.forEach((compound) => {
    addNode({
      id: compound.compound_id,
      label: compound.name || compound.compound_id,
      type: "metabolite",
    });
  });

  return {
    nodes: Array.from(nodes.values()),
    edges: Array.from(edges.values()),
  };
}
