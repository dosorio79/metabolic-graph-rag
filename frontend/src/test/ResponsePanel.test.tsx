import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ResponsePanel from "@/components/ResponsePanel";

describe("ResponsePanel", () => {
  it("shows placeholder when no answer", () => {
    render(<ResponsePanel answer="" supportingSources={[]} contextSources={[]} isLoading={false} />);
    expect(screen.getByText("Response will appear here")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(<ResponsePanel answer="" supportingSources={[]} contextSources={[]} isLoading={true} />);
    expect(screen.getByText("Retrieving from knowledge graph…")).toBeInTheDocument();
  });

  it("renders answer text and split evidence sections", () => {
    render(
      <ResponsePanel
        answer="Test answer about metabolism"
        supportingSources={[{ id: "compound:C00022", label: "Compound Pyruvate", href: "https://www.kegg.jp/entry/C00022" }]}
        contextSources={[{ id: "pathway:map00010", label: "Pathway map00010", href: "https://www.kegg.jp/entry/map00010" }]}
        isLoading={false}
      />
    );
    expect(screen.getByText("Test answer about metabolism")).toBeInTheDocument();
    expect(screen.getByText("Supporting Evidence")).toBeInTheDocument();
    expect(screen.getByText("Retrieved Context")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open source compound pyruvate/i })).toHaveAttribute(
      "href",
      "https://www.kegg.jp/entry/C00022",
    );
  });

  it("renders error message", () => {
    render(
      <ResponsePanel
        answer=""
        supportingSources={[]}
        contextSources={[]}
        isLoading={false}
        error="Failed to query RAG API"
      />
    );
    expect(screen.getByText("Failed to query RAG API")).toBeInTheDocument();
  });
});
