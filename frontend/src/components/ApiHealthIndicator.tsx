import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "@/services/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

type Status = "checking" | "healthy" | "degraded" | "offline";

const ApiHealthIndicator = () => {
  const [status, setStatus] = useState<Status>("checking");
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const check = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
      const apiOk = h.api_status.status === "ok";
      const neo4jOk = h.neo4j_status.status === "ok";
      setStatus(apiOk && neo4jOk ? "healthy" : apiOk ? "degraded" : "offline");
    } catch {
      setHealth(null);
      setStatus("offline");
    }
  };

  useEffect(() => {
    check();
    const id = setInterval(check, 30_000);
    return () => clearInterval(id);
  }, []);

  const colors: Record<Status, string> = {
    checking: "bg-muted-foreground",
    healthy: "bg-emerald-500",
    degraded: "bg-amber-500",
    offline: "bg-destructive",
  };

  const labels: Record<Status, string> = {
    checking: "Checking API…",
    healthy: "API & Neo4j connected",
    degraded: `API ok · Neo4j: ${health?.neo4j_status.detail ?? "issue"}`,
    offline: "API unreachable",
  };

  return (
    <TooltipProvider delayDuration={200}>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={check}
            className="flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:text-foreground"
            aria-label={labels[status]}
          >
            <span className={`inline-block h-2 w-2 rounded-full ${colors[status]} ${status === "checking" ? "animate-pulse" : ""}`} />
            <span className="hidden sm:inline">
              {status === "healthy" ? "Connected" : status === "checking" ? "Checking…" : status === "degraded" ? "Degraded" : "Offline"}
            </span>
          </button>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="text-xs">
          {labels[status]}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default ApiHealthIndicator;
