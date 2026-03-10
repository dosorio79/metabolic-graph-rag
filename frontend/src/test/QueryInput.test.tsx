import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import QueryInput from "@/components/QueryInput";

describe("QueryInput", () => {
  it("renders input and button", () => {
    render(<QueryInput onSubmit={() => {}} isLoading={false} />);
    expect(screen.getByPlaceholderText(/metabolic pathways/i)).toBeInTheDocument();
    expect(screen.getByText("Query")).toBeInTheDocument();
  });

  it("calls onSubmit with query text", () => {
    const onSubmit = vi.fn();
    render(<QueryInput onSubmit={onSubmit} isLoading={false} />);
    const input = screen.getByPlaceholderText(/metabolic pathways/i);
    fireEvent.change(input, { target: { value: "glycolysis" } });
    fireEvent.submit(input.closest("form")!);
    expect(onSubmit).toHaveBeenCalledWith("glycolysis");
  });

  it("disables input when loading", () => {
    render(<QueryInput onSubmit={() => {}} isLoading={true} />);
    expect(screen.getByPlaceholderText(/metabolic pathways/i)).toBeDisabled();
    expect(screen.getByText("Querying…")).toBeInTheDocument();
  });

  it("does not submit empty query", () => {
    const onSubmit = vi.fn();
    render(<QueryInput onSubmit={onSubmit} isLoading={false} />);
    fireEvent.submit(screen.getByPlaceholderText(/metabolic pathways/i).closest("form")!);
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
