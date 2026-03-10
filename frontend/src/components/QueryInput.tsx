import { useState, FormEvent } from "react";
import { Search, ArrowRight, Loader2 } from "lucide-react";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

const QueryInput = ({ onSubmit, isLoading }: QueryInputProps) => {
  const [query, setQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div
        className={`glass-card glow-ring relative flex items-center transition-all duration-300 ${
          isFocused ? "ring-2 ring-ring/40" : ""
        }`}
      >
        <Search className={`absolute left-4 h-4 w-4 transition-colors duration-200 ${isFocused ? "text-primary" : "text-muted-foreground"}`} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Ask about metabolic pathways… e.g. 'Describe glycolysis'"
          className="h-12 w-full rounded-lg bg-transparent pl-11 pr-28 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none font-sans"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 flex h-8 items-center gap-1.5 rounded-md bg-primary px-4 text-xs font-medium text-primary-foreground transition-all duration-200 hover:bg-primary/90 hover:shadow-lg hover:shadow-primary/20 active:scale-95 disabled:opacity-40 disabled:hover:shadow-none"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-3 w-3 animate-spin" />
              Querying…
            </>
          ) : (
            <>
              Query
              <ArrowRight className="h-3 w-3" />
            </>
          )}
        </button>
      </div>
    </form>
  );
};

export default QueryInput;
