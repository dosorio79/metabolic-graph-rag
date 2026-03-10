import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import ResponsePanel from "@/components/ResponsePanel";

describe("ResponsePanel", () => {
  it("shows placeholder when no answer", () => {
    render(<ResponsePanel answer="" sources={[]} isLoading={false} />);
    expect(screen.getByText("Response will appear here")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(<ResponsePanel answer="" sources={[]} isLoading={true} />);
    expect(screen.getByText("Retrieving from knowledge graph…")).toBeInTheDocument();
  });

  it("renders answer text", () => {
    render(
      <ResponsePanel answer="Test answer about metabolism" sources={["KEGG:123"]} isLoading={false} />
    );
    expect(screen.getByText("Test answer about metabolism")).toBeInTheDocument();
    expect(screen.getByText("KEGG:123")).toBeInTheDocument();
  });

  it("renders error message", () => {
    render(
      <ResponsePanel
        answer=""
        sources={[]}
        isLoading={false}
        error="Failed to query RAG API"
      />
    );
    expect(screen.getByText("Failed to query RAG API")).toBeInTheDocument();
  });
});
