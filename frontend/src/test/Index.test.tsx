import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Index from "@/pages/Index";
import type { RAGResponse } from "@/services/api";

const {
  queryRagMock,
  fetchReactionMock,
  fetchEntityByIdMock,
  buildGraphFromRagMock,
} = vi.hoisted(() => ({
  queryRagMock: vi.fn(),
  fetchReactionMock: vi.fn(),
  fetchEntityByIdMock: vi.fn(),
  buildGraphFromRagMock: vi.fn(),
}));

vi.mock("@/services/api", async () => {
  const actual = await vi.importActual<typeof import("@/services/api")>("@/services/api");
  return {
    ...actual,
    queryRag: queryRagMock,
    fetchReaction: fetchReactionMock,
    fetchEntityById: fetchEntityByIdMock,
  };
});

vi.mock("@/services/graph", async () => {
  const actual = await vi.importActual<typeof import("@/services/graph")>("@/services/graph");
  return {
    ...actual,
    buildGraphFromRag: buildGraphFromRagMock,
  };
});

vi.mock("@/components/GraphViewer", () => ({
  default: () => <div data-testid="graph-viewer">graph</div>,
}));

vi.mock("@/components/ApiHealthIndicator", () => ({
  default: () => <div data-testid="api-health-indicator" />,
}));

vi.mock("@/components/ThemeToggle", () => ({
  default: () => <div data-testid="theme-toggle" />,
}));

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

function mockRagResponse(): RAGResponse {
  return {
    answer: "Pyruvate can be produced by R00010.",
    interpretation: {
      entity_type: "compound",
      entity_id: "C00022",
      entity_name: "pyruvate",
      intent: "producers",
      confidence: 0.9,
    },
    context: "context",
    reactions: [{ reaction_id: "R00010", name: "Reaction 10" }],
    compounds: [{ compound_id: "C00022", name: "Pyruvate" }],
    enzymes: ["1.1.1.1"],
    trace: {
      reaction_ids: ["R00010"],
      compound_ids: ["C00022"],
      pathway_ids: [],
      enzyme_ecs: ["1.1.1.1"],
    },
  };
}

describe("Index page", () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    queryRagMock.mockReset();
    fetchReactionMock.mockReset();
    fetchEntityByIdMock.mockReset();
    buildGraphFromRagMock.mockReset();
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it("submits query, shows loading, then renders answer", async () => {
    const d = deferred<RAGResponse>();
    queryRagMock.mockReturnValueOnce(d.promise);
    buildGraphFromRagMock.mockResolvedValueOnce({ nodes: [], edges: [] });

    render(<Index />);

    fireEvent.change(screen.getByPlaceholderText(/ask about metabolic pathways/i), {
      target: { value: "How is pyruvate produced?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /query/i }));

    expect(await screen.findByText("Retrieving from knowledge graph…")).toBeInTheDocument();

    d.resolve(mockRagResponse());

    expect(await screen.findByText("Pyruvate can be produced by R00010.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open source reaction r00010: reaction 10/i })).toBeInTheDocument();
    await waitFor(() => {
      expect(queryRagMock).toHaveBeenCalledWith("How is pyruvate produced?");
    });
  });

  it("renders API error when query fails", async () => {
    queryRagMock.mockRejectedValueOnce(new Error("Backend unavailable"));

    render(<Index />);

    fireEvent.change(screen.getByPlaceholderText(/ask about metabolic pathways/i), {
      target: { value: "Any query" },
    });
    fireEvent.click(screen.getByRole("button", { name: /query/i }));

    expect(await screen.findByText("Backend unavailable")).toBeInTheDocument();
  });
});
