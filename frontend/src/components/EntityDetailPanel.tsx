import { X, FlaskConical, ArrowRightLeft, Route, Loader2 } from "lucide-react";
import type { EntityDetail } from "@/services/api";

interface EntityDetailPanelProps {
  detail: EntityDetail | null;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
  onNavigate?: (id: string) => void;
}

const IdChip = ({
  id,
  name,
  onClick,
}: {
  id: string;
  name?: string | null;
  onClick?: () => void;
}) => (
  <button
    onClick={onClick}
    className="inline-flex items-center gap-1 rounded-md bg-accent/80 backdrop-blur-sm px-2 py-0.5 text-[11px] font-mono text-accent-foreground border border-accent-foreground/10 transition-all duration-200 hover:bg-accent hover:shadow-sm hover:scale-[1.02] active:scale-95"
  >
    <span className="font-semibold">{id}</span>
    {name && <span className="text-muted-foreground">· {name}</span>}
  </button>
);

const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h4 className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
    {children}
  </h4>
);

const EntityDetailPanel = ({
  detail,
  isLoading,
  error,
  onClose,
  onNavigate,
}: EntityDetailPanelProps) => {
  if (!detail && !isLoading && !error) return null;

  const icon =
    detail?.type === "compound" ? FlaskConical :
    detail?.type === "reaction" ? ArrowRightLeft :
    Route;
  const Icon = isLoading ? Loader2 : icon;

  return (
    <div className="absolute top-0 right-0 bottom-0 w-80 z-40 glass-elevated animate-slide-in-right overflow-auto">
      {/* Header */}
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border/50 bg-card/90 backdrop-blur-md px-4 py-3">
        <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
          <Icon className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          {isLoading
            ? "Loading…"
            : detail
              ? detail.type.charAt(0).toUpperCase() + detail.type.slice(1)
              : "Error"}
        </div>
        <button
          onClick={onClose}
          className="flex h-6 w-6 items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-accent transition-all duration-200 active:scale-90"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="p-4 text-xs font-mono space-y-4">
        {error && (
          <p className="text-destructive animate-fade-in">{error}</p>
        )}

        {detail?.type === "compound" && (
          <div className="animate-fade-in space-y-4">
            <div>
              <p className="text-foreground text-sm font-semibold">{detail.data.name ?? detail.data.compound_id}</p>
              <p className="text-muted-foreground mt-0.5">{detail.data.compound_id}</p>
            </div>
            {detail.data.consuming_reactions.length > 0 && (
              <div>
                <SectionTitle>Consuming Reactions</SectionTitle>
                <div className="flex flex-wrap gap-1">
                  {detail.data.consuming_reactions.map((r) => (
                    <IdChip key={r.reaction_id} id={r.reaction_id} name={r.name} onClick={() => onNavigate?.(r.reaction_id)} />
                  ))}
                </div>
              </div>
            )}
            {detail.data.producing_reactions.length > 0 && (
              <div>
                <SectionTitle>Producing Reactions</SectionTitle>
                <div className="flex flex-wrap gap-1">
                  {detail.data.producing_reactions.map((r) => (
                    <IdChip key={r.reaction_id} id={r.reaction_id} name={r.name} onClick={() => onNavigate?.(r.reaction_id)} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {detail?.type === "reaction" && (
          <div className="animate-fade-in space-y-4">
            <div>
              <p className="text-foreground text-sm font-semibold">{detail.data.name ?? detail.data.reaction_id}</p>
              <p className="text-muted-foreground mt-0.5">{detail.data.reaction_id}</p>
            </div>
            {detail.data.equation && (
              <div>
                <SectionTitle>Equation</SectionTitle>
                <p className="text-foreground bg-muted/50 rounded-md p-2 text-[11px] leading-relaxed border border-border/30">{detail.data.equation}</p>
              </div>
            )}
            {detail.data.definition && (
              <div>
                <SectionTitle>Definition</SectionTitle>
                <p className="text-foreground">{detail.data.definition}</p>
              </div>
            )}
            <div>
              <SectionTitle>Direction</SectionTitle>
              <p className="text-foreground">{detail.data.reversible ? "⇌ Reversible" : "→ Irreversible"}</p>
            </div>
            {detail.data.substrates.length > 0 && (
              <div>
                <SectionTitle>Substrates</SectionTitle>
                <div className="flex flex-wrap gap-1">
                  {detail.data.substrates.map((s) => (
                    <IdChip
                      key={s.compound_id}
                      id={s.compound_id}
                      name={s.name ? `${s.name} ×${s.coef}` : `×${s.coef}`}
                      onClick={() => onNavigate?.(s.compound_id)}
                    />
                  ))}
                </div>
              </div>
            )}
            {detail.data.products.length > 0 && (
              <div>
                <SectionTitle>Products</SectionTitle>
                <div className="flex flex-wrap gap-1">
                  {detail.data.products.map((p) => (
                    <IdChip
                      key={p.compound_id}
                      id={p.compound_id}
                      name={p.name ? `${p.name} ×${p.coef}` : `×${p.coef}`}
                      onClick={() => onNavigate?.(p.compound_id)}
                    />
                  ))}
                </div>
              </div>
            )}
            {detail.data.enzymes.length > 0 && (
              <div>
                <SectionTitle>Enzymes (EC)</SectionTitle>
                <div className="flex flex-wrap gap-1">
                  {detail.data.enzymes.map((ec) => (
                    <span key={ec} className="rounded-md bg-accent/80 px-2 py-0.5 text-[11px] font-mono text-accent-foreground border border-accent-foreground/10">
                      {ec}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {detail?.type === "pathway" && (
          <div className="animate-fade-in space-y-4">
            <div>
              <p className="text-foreground text-sm font-semibold">{detail.data.name ?? detail.data.pathway_id}</p>
              <p className="text-muted-foreground mt-0.5">{detail.data.pathway_id}</p>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[
                { label: "Reactions", value: detail.data.reaction_count },
                { label: "Compounds", value: detail.data.compound_count },
                { label: "Enzymes", value: detail.data.enzyme_count },
              ].map((stat, i) => (
                <div
                  key={stat.label}
                  className="animate-scale-in rounded-lg border border-border/50 bg-muted/30 p-2.5 text-center backdrop-blur-sm"
                  style={{ animationDelay: `${i * 0.08}s`, opacity: 0 }}
                >
                  <p className="text-foreground text-base font-semibold">{stat.value}</p>
                  <p className="text-[9px] text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
            {detail.data.reactions.length > 0 && (
              <div>
                <SectionTitle>Reactions</SectionTitle>
                <div className="flex flex-wrap gap-1 max-h-40 overflow-auto">
                  {detail.data.reactions.map((r) => (
                    <IdChip key={r.reaction_id} id={r.reaction_id} name={r.name} onClick={() => onNavigate?.(r.reaction_id)} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EntityDetailPanel;
