import { useEffect, useRef, useCallback, useState } from "react";
import cytoscape, { Core } from "cytoscape";
import type { GraphNode, GraphEdge } from "@/services/mockApi";
import { ZoomIn, ZoomOut, Maximize, RotateCcw, Search, X } from "lucide-react";

const TYPE_LABELS: Record<GraphNode["type"], string> = {
  metabolite: "Metabolite",
  enzyme: "Enzyme",
  pathway: "Pathway",
  reaction: "Reaction",
  gene: "Gene",
};

interface GraphViewerProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (label: string) => void;
  onNodeIdClick?: (id: string) => void;
  detailPanel?: React.ReactNode;
}

const NODE_COLORS: Record<GraphNode["type"], string> = {
  metabolite: "hsl(174, 62%, 45%)",
  enzyme: "hsl(220, 60%, 60%)",
  pathway: "hsl(40, 90%, 55%)",
  reaction: "hsl(0, 72%, 55%)",
  gene: "hsl(280, 50%, 55%)",
};

const NODE_SHAPES: Record<GraphNode["type"], string> = {
  metabolite: "ellipse",
  enzyme: "round-rectangle",
  pathway: "diamond",
  reaction: "triangle",
  gene: "hexagon",
};

const GraphViewer = ({ nodes, edges, onNodeClick, onNodeIdClick, detailPanel }: GraphViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [tooltip, setTooltip] = useState<{
    x: number;
    y: number;
    label: string;
    type: GraphNode["type"];
    connections: number;
    neighbors: string[];
  } | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTypeFilters, setActiveTypeFilters] = useState<Set<GraphNode["type"]>>(new Set());

  const buildElements = useCallback(() => {
    const cyNodes = nodes.map((n) => ({
      data: {
        id: n.id,
        label: n.label,
        type: n.type,
      },
    }));

    const cyEdges = edges.map((e, i) => ({
      data: {
        id: `e${i}`,
        source: e.source,
        target: e.target,
        label: e.label,
      },
    }));

    return [...cyNodes, ...cyEdges];
  }, [nodes, edges]);

  useEffect(() => {
    setSearchQuery("");
    setActiveTypeFilters(new Set());
    if (!containerRef.current || nodes.length === 0) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: buildElements(),
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "bottom",
            "text-halign": "center",
            "font-size": "11px",
            "font-family": "Inter, sans-serif",
            color: "#94a3b8",
            "text-margin-y": 6,
            width: 36,
            height: 36,
            "border-width": 2,
            "border-color": "#1e293b",
            "background-color": (ele: any) => NODE_COLORS[ele.data("type") as GraphNode["type"]] || "#64748b",
            shape: (ele: any) => NODE_SHAPES[ele.data("type") as GraphNode["type"]] || "ellipse",
            cursor: "pointer",
          } as any,
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#475569",
            "target-arrow-color": "#475569",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": "9px",
            "font-family": "Inter, sans-serif",
            color: "#64748b",
            "text-rotation": "autorotate",
            "text-margin-y": -8,
          } as any,
        },
        {
          selector: "node:active, node:selected",
          style: {
            "border-color": "hsl(174, 62%, 45%)",
            "border-width": 3,
          },
        },
        {
          selector: "node.hover",
          style: {
            width: 44,
            height: 44,
            "border-width": 3,
            "border-color": "#f8fafc",
            "z-index": 10,
          },
        },
        {
          selector: ".hover-neighbor",
          style: {
            "border-width": 2,
            "border-color": "#94a3b8",
            "line-color": "#94a3b8",
            "target-arrow-color": "#94a3b8",
            width: 2,
          } as any,
        },
        {
          selector: "node.search-match",
          style: {
            width: 46,
            height: 46,
            "border-width": 3,
            "border-color": "#f8fafc",
            "z-index": 10,
            "font-weight": "bold",
            color: "#f8fafc",
          },
        },
        {
          selector: "node.search-dimmed",
          style: {
            opacity: 0.2,
          },
        },
        {
          selector: "edge.search-dimmed",
          style: {
            opacity: 0.1,
          },
        },
      ],
      layout: {
        name: "cose",
        animate: true,
        animationDuration: 600,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 140,
        edgeElasticity: () => 100,
        gravity: 0.25,
        numIter: 1000,
        padding: 50,
        nestingFactor: 1.2,
        componentSpacing: 60,
      } as any,
      minZoom: 0.3,
      maxZoom: 3,
    });

    cyRef.current = cy;

    // Hover tooltip
    cy.on("mouseover", "node", (evt) => {
      const node = evt.target;
      const pos = node.renderedPosition();
      const neighbors = node.neighborhood("node").map((n: any) => n.data("label"));
      setTooltip({
        x: pos.x,
        y: pos.y,
        label: node.data("label"),
        type: node.data("type") as GraphNode["type"],
        connections: node.degree(false),
        neighbors: neighbors.slice(0, 5),
      });
      // Highlight connected elements
      node.addClass("hover");
      node.neighborhood().addClass("hover-neighbor");
    });

    cy.on("mouseout", "node", () => {
      setTooltip(null);
      cy.elements().removeClass("hover hover-neighbor");
    });

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      const label = node.data("label");
      const id = node.data("id");
      if (onNodeIdClick && id) {
        onNodeIdClick(id);
      } else if (label && onNodeClick) {
        onNodeClick(label);
      }
    });

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, buildElements]);

  // Search & filter highlighting
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    const query = searchQuery.toLowerCase().trim();
    const hasFilter = activeTypeFilters.size > 0;
    const hasSearch = query.length > 0;

    if (!hasSearch && !hasFilter) {
      cy.elements().removeClass("search-match search-dimmed");
      return;
    }

    cy.nodes().forEach((node: any) => {
      const label: string = node.data("label")?.toLowerCase() || "";
      const type: GraphNode["type"] = node.data("type");
      const matchesSearch = !hasSearch || label.includes(query);
      const matchesType = !hasFilter || activeTypeFilters.has(type);

      if (matchesSearch && matchesType) {
        node.removeClass("search-dimmed").addClass("search-match");
      } else {
        node.removeClass("search-match").addClass("search-dimmed");
      }
    });

    cy.edges().forEach((edge: any) => {
      const src = edge.source();
      const tgt = edge.target();
      if (src.hasClass("search-match") || tgt.hasClass("search-match")) {
        edge.removeClass("search-dimmed");
      } else {
        edge.addClass("search-dimmed");
      }
    });
  }, [searchQuery, activeTypeFilters]);

  const isEmpty = nodes.length === 0;

  const handleZoomIn = () => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  };

  const handleZoomOut = () => {
    const cy = cyRef.current;
    if (cy) cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } });
  };

  const handleFit = () => {
    cyRef.current?.fit(undefined, 40);
  };

  const handleRelayout = () => {
    const cy = cyRef.current;
    if (cy) {
      cy.layout({
        name: "cose",
        animate: true,
        animationDuration: 600,
        nodeRepulsion: () => 8000,
        idealEdgeLength: () => 140,
        edgeElasticity: () => 100,
        gravity: 0.25,
        numIter: 1000,
        padding: 50,
        nestingFactor: 1.2,
        componentSpacing: 60,
      } as any).run();
    }
  };

  return (
    <div className="graph-container relative h-full w-full overflow-hidden">
      {isEmpty && (
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm text-muted-foreground font-mono">
            Graph will appear here
          </p>
        </div>
      )}
      <div ref={containerRef} className="h-full w-full" />
      {!isEmpty && (
        <>
          {/* Search & filter bar */}
          <div className="absolute top-3 left-3 right-14 flex items-center gap-2">
            <div className="relative flex-1 max-w-[220px]">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search nodes…"
                className="h-7 w-full rounded-md bg-card/80 backdrop-blur-sm border border-border pl-7 pr-7 text-xs font-mono text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            <div className="flex gap-1">
              {(Object.keys(NODE_COLORS) as GraphNode["type"][]).map((type) => {
                const active = activeTypeFilters.has(type);
                return (
                  <button
                    key={type}
                    onClick={() => {
                      setActiveTypeFilters((prev) => {
                        const next = new Set(prev);
                        if (next.has(type)) next.delete(type);
                        else next.add(type);
                        return next;
                      });
                    }}
                    className={`flex items-center gap-1 rounded-md px-2 h-6 text-[10px] font-mono border transition-colors ${
                      active
                        ? "bg-foreground/10 border-foreground/30 text-foreground"
                        : "bg-card/60 backdrop-blur-sm border-border text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <span
                      className="inline-block h-2 w-2 rounded-sm"
                      style={{ backgroundColor: NODE_COLORS[type] }}
                    />
                    {type}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="absolute top-3 right-3 flex flex-col gap-1">
            {[
              { icon: ZoomIn, onClick: handleZoomIn, title: "Zoom in" },
              { icon: ZoomOut, onClick: handleZoomOut, title: "Zoom out" },
              { icon: Maximize, onClick: handleFit, title: "Fit to view" },
              { icon: RotateCcw, onClick: handleRelayout, title: "Re-layout" },
            ].map(({ icon: Icon, onClick, title }) => (
              <button
                key={title}
                onClick={onClick}
                title={title}
                className="flex h-7 w-7 items-center justify-center rounded-md bg-card/80 backdrop-blur-sm border border-border text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
              >
                <Icon className="h-3.5 w-3.5" />
              </button>
            ))}
          </div>
          <div className="absolute bottom-3 left-3 flex gap-3 text-[10px] font-mono text-muted-foreground">
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <span key={type} className="flex items-center gap-1">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-sm"
                  style={{ backgroundColor: color }}
                />
                {type}
              </span>
            ))}
          </div>
          {tooltip && (
            <div
              className="absolute z-50 pointer-events-none rounded-lg border border-border bg-card/95 backdrop-blur-md p-3 shadow-xl text-xs font-mono max-w-[200px]"
              style={{
                left: tooltip.x + 16,
                top: tooltip.y - 10,
                transform: "translateY(-100%)",
              }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-sm shrink-0"
                  style={{ backgroundColor: NODE_COLORS[tooltip.type] }}
                />
                <span className="font-semibold text-foreground truncate">{tooltip.label}</span>
              </div>
              <div className="text-muted-foreground space-y-0.5">
                <p>Type: <span className="text-foreground">{TYPE_LABELS[tooltip.type]}</span></p>
                <p>Connections: <span className="text-foreground">{tooltip.connections}</span></p>
                {tooltip.neighbors.length > 0 && (
                  <div className="mt-1 pt-1 border-t border-border">
                    <p className="mb-0.5">Linked to:</p>
                    {tooltip.neighbors.map((n, i) => (
                      <p key={i} className="text-foreground truncate">• {n}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
          {detailPanel}
        </>
      )}
    </div>
  );
};

export default GraphViewer;
