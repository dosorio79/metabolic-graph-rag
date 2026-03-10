import { describe, it, expect, vi } from "vitest";
import { queryGraphRAG } from "@/services/mockApi";

describe("mockApi", () => {
  it("returns glycolysis response for glycolysis query", async () => {
    const result = await queryGraphRAG("Tell me about glycolysis");
    expect(result.answer).toContain("Glycolysis");
    expect(result.nodes.length).toBeGreaterThan(0);
    expect(result.edges.length).toBeGreaterThan(0);
    expect(result.sources.length).toBeGreaterThan(0);
  });

  it("returns glycolysis response for glucose query", async () => {
    const result = await queryGraphRAG("What happens to glucose?");
    expect(result.answer).toContain("Glycolysis");
  });

  it("returns default TCA response for unknown queries", async () => {
    const result = await queryGraphRAG("Tell me about something else");
    expect(result.answer).toContain("citric acid cycle");
  });

  it("response has valid graph structure", async () => {
    const result = await queryGraphRAG("glycolysis");
    const nodeIds = new Set(result.nodes.map((n) => n.id));

    for (const edge of result.edges) {
      expect(nodeIds.has(edge.source)).toBe(true);
      expect(nodeIds.has(edge.target)).toBe(true);
    }
  });

  it("nodes have valid types", async () => {
    const result = await queryGraphRAG("glycolysis");
    const validTypes = ["metabolite", "enzyme", "pathway", "reaction", "gene"];
    for (const node of result.nodes) {
      expect(validTypes).toContain(node.type);
    }
  });
});
