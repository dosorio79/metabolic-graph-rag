import { describe, it, expect, vi, afterEach } from "vitest";
import { queryRag, fetchHealth } from "@/services/api";

const fetchMock = vi.fn();

vi.stubGlobal("fetch", fetchMock);

afterEach(() => {
  fetchMock.mockReset();
});

describe("api service", () => {
  it("calls /rag/query and returns typed payload", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        answer: "Pyruvate can be produced by R00200.",
        interpretation: {
          entity_type: "compound",
          entity_id: "C00022",
          entity_name: "pyruvate",
          intent: "producers",
          confidence: 0.92,
        },
        context: "Compound: Pyruvate",
        reactions: [{ reaction_id: "R00200", name: "Example Reaction" }],
        compounds: [{ compound_id: "C00022", name: "Pyruvate" }],
        enzymes: ["1.1.1.1"],
        trace: {
          reaction_ids: ["R00200"],
          compound_ids: ["C00022"],
          pathway_ids: [],
          enzyme_ecs: ["1.1.1.1"],
        },
      }),
    });

    const res = await queryRag("How is pyruvate produced?");
    expect(res.answer).toContain("Pyruvate");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/rag/query",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
  });

  it("throws parsed API error details", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      statusText: "Bad Request",
      json: async () => ({ detail: "question must not be empty" }),
    });

    await expect(queryRag("")).rejects.toThrow("question must not be empty");
  });

  it("throws fallback status text when response body is not JSON", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      statusText: "Service Unavailable",
      json: async () => {
        throw new Error("invalid json");
      },
    });

    await expect(fetchHealth()).rejects.toThrow("Service Unavailable");
  });
});
