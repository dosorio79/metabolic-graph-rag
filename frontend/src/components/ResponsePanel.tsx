export interface ResponseSource {
  id: string;
  label: string;
  href?: string;
}

interface ResponsePanelProps {
  answer: string;
  supportingSources: ResponseSource[];
  contextSources: ResponseSource[];
  isLoading: boolean;
  error?: string | null;
}

const TypingIndicator = () => (
  <div className="flex items-center gap-3">
    <div className="flex items-center gap-1">
      <span className="typing-dot inline-block h-2 w-2 rounded-full bg-primary" />
      <span className="typing-dot inline-block h-2 w-2 rounded-full bg-primary" />
      <span className="typing-dot inline-block h-2 w-2 rounded-full bg-primary" />
    </div>
    <span className="text-sm text-muted-foreground">Retrieving from knowledge graph…</span>
  </div>
);

const ResponsePanel = ({ answer, supportingSources, contextSources, isLoading, error }: ResponsePanelProps) => {
  if (isLoading) {
    return (
      <div className="response-box flex h-full flex-col p-5">
        <h2 className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Response
        </h2>
        <TypingIndicator />
      </div>
    );
  }

  if (error) {
    return (
      <div className="response-box flex h-full flex-col p-5">
        <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Response
        </h2>
        <p className="text-sm text-destructive">{error}</p>
      </div>
    );
  }

  if (!answer) {
    return (
      <div className="response-box flex h-full flex-col items-center justify-center p-5">
        <div className="flex flex-col items-center gap-2 text-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
            <span className="text-lg">🧬</span>
          </div>
          <p className="text-sm text-muted-foreground font-mono">
            Response will appear here
          </p>
          <p className="text-xs text-muted-foreground/60">
            Try asking about glycolysis, TCA cycle, or specific compounds
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="response-box flex h-full flex-col p-5 overflow-auto">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        Response
      </h2>
      <p className="animate-fade-in text-sm leading-relaxed text-card-foreground">{answer}</p>
      {(supportingSources.length > 0 || contextSources.length > 0) && (
        <div className="mt-4 border-t border-border/50 pt-3 animate-fade-in" style={{ animationDelay: "0.15s", opacity: 0 }}>
          {supportingSources.length > 0 && (
            <>
              <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Supporting Evidence
              </h3>
              <p className="mb-2 text-[11px] text-muted-foreground">
                Open representative KEGG entities selected to support the answer directly.
              </p>
              <div className="flex flex-wrap gap-1.5">
                {supportingSources.map((source, i) => (
                  <a
                    key={source.id}
                    href={source.href}
                    target={source.href ? "_blank" : undefined}
                    rel={source.href ? "noreferrer" : undefined}
                    className="animate-scale-in rounded-md bg-accent/80 backdrop-blur-sm px-2.5 py-1 text-[11px] font-mono text-accent-foreground border border-accent-foreground/10 transition-all duration-200 hover:bg-accent hover:shadow-sm"
                    style={{ animationDelay: `${0.2 + i * 0.05}s`, opacity: 0 }}
                    aria-label={`Open source ${source.label}`}
                  >
                    {source.label}
                  </a>
                ))}
              </div>
            </>
          )}
          {contextSources.length > 0 && (
            <div className={supportingSources.length > 0 ? "mt-4" : ""}>
              <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Retrieved Context
              </h3>
              <p className="mb-2 text-[11px] text-muted-foreground">
                These entities come from the wider retrieval result used for graph exploration and follow-up inspection.
              </p>
              <div className="flex flex-wrap gap-1.5">
                {contextSources.map((source, i) => (
                  <a
                    key={source.id}
                    href={source.href}
                    target={source.href ? "_blank" : undefined}
                    rel={source.href ? "noreferrer" : undefined}
                    className="animate-scale-in rounded-md border border-border bg-background/50 px-2.5 py-1 text-[11px] font-mono text-muted-foreground transition-all duration-200 hover:bg-muted/40"
                    style={{ animationDelay: `${0.2 + (supportingSources.length + i) * 0.05}s`, opacity: 0 }}
                    aria-label={`Open source ${source.label}`}
                  >
                    {source.label}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResponsePanel;
