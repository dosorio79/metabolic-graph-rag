import { describe, it, expect } from "vitest";
import { buildGraphFromRag } from "@/services/graph";
import type { RAGResponse, ReactionResponse } from "@/services/api";

function makeResponse(overrides?: Partial<RAGResponse>): RAGResponse {
  return {
    answer: "test answer",
    interpretation: {
      entity_type: "compound",
      entity_id: "C00022",
      entity_name: "pyruvate",
      intent: "producers",
      confidence: 0.9,
    },
    context: "test context",
    reactions: [{ reaction_id: "R00010", name: "Reaction 10" }],
    compounds: [{ compound_id: "C00022", name: "Pyruvate" }],
    enzymes: ["1.1.1.1"],
    trace: {
      reaction_ids: ["R00010"],
      compound_ids: ["C00022"],
      pathway_ids: ["hsa00010"],
      enzyme_ecs: ["1.1.1.1"],
    },
    ...overrides,
  };
}

describe("buildGraphFromRag", () => {
  it("builds graph relationships from reaction detail payloads", async () => {
    const fetchReactionDetail = async (): Promise<ReactionResponse> => ({
      reaction_id: "R00010",
      name: "Reaction 10",
      reversible: false,
      substrates: [{ compound_id: "C00001", name: "H2O", coef: 1 }],
      products: [{ compound_id: "C00022", name: "Pyruvate", coef: 2 }],
      enzymes: ["1.1.1.1"],
    });
    const graph = await buildGraphFromRag(makeResponse(), { fetchReactionDetail });
    const nodeIds = new Set(graph.nodes.map((node) => node.id));

    expect(nodeIds.has("hsa00010")).toBe(true);
    expect(nodeIds.has("R00010")).toBe(true);
    expect(nodeIds.has("1.1.1.1")).toBe(true);
    expect(nodeIds.has("C00001")).toBe(true);
    expect(nodeIds.has("C00022")).toBe(true);
    expect(
      graph.edges.some(
        (edge) =>
          edge.source === "hsa00010" &&
          edge.target === "R00010" &&
          edge.relationship === "HAS_REACTION",
      ),
    ).toBe(true);
    expect(
      graph.edges.some(
        (edge) =>
          edge.source === "C00001" &&
          edge.target === "R00010" &&
          edge.relationship === "CONSUMED_BY",
      ),
    ).toBe(true);
    expect(
      graph.edges.some(
        (edge) =>
          edge.source === "R00010" &&
          edge.target === "C00022" &&
          edge.relationship === "PRODUCES",
      ),
    ).toBe(true);
    expect(
      graph.edges.some(
        (edge) =>
          edge.source === "1.1.1.1" &&
          edge.target === "R00010" &&
          edge.relationship === "CATALYZES",
      ),
    ).toBe(true);
  });

  it("includes interpreted pathway entity id when trace is empty", async () => {
    const graph = await buildGraphFromRag(
      makeResponse({
        interpretation: {
          entity_type: "pathway",
          entity_id: "hsa00020",
          entity_name: "TCA cycle",
          intent: "summary",
          confidence: 0.8,
        },
        trace: {
          reaction_ids: [],
          compound_ids: [],
          pathway_ids: [],
          enzyme_ecs: [],
        },
      }),
      {
        fetchReactionDetail: async () => ({
          reaction_id: "R00010",
          name: "Reaction 10",
          reversible: false,
          substrates: [],
          products: [],
          enzymes: [],
        }),
      },
    );

    expect(
      graph.nodes.some((node) => node.id === "hsa00020" && node.type === "pathway"),
    ).toBe(true);
  });

  it("keeps focal compounds when reaction detail fetch fails", async () => {
    const graph = await buildGraphFromRag(makeResponse(), {
      fetchReactionDetail: async () => {
        throw new Error("network");
      },
    });

    expect(graph.nodes.some((node) => node.id === "C00022" && node.type === "metabolite")).toBe(
      true,
    );
  });
});
