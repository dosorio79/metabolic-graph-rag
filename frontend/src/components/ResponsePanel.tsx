interface ResponsePanelProps {
  answer: string;
  sources: string[];
  isLoading: boolean;
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

const ResponsePanel = ({ answer, sources, isLoading }: ResponsePanelProps) => {
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
      {sources.length > 0 && (
        <div className="mt-4 border-t border-border/50 pt-3 animate-fade-in" style={{ animationDelay: "0.15s", opacity: 0 }}>
          <h3 className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            Sources
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {sources.map((s, i) => (
              <span
                key={s}
                className="animate-scale-in rounded-md bg-accent/80 backdrop-blur-sm px-2.5 py-1 text-[11px] font-mono text-accent-foreground border border-accent-foreground/10 transition-all duration-200 hover:bg-accent hover:shadow-sm cursor-default"
                style={{ animationDelay: `${0.2 + i * 0.05}s`, opacity: 0 }}
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResponsePanel;
