import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { ChevronDown, ArrowRight } from "lucide-react";
import type { Recommendation } from "@/lib/recommend";
import { STAGE_MAP } from "@/lib/frameworks";
import { cn } from "@/lib/utils";

function priority(score: number) {
  if (score >= 85) return "Start here";
  if (score >= 70) return "High relevance";
  if (score >= 55) return "Worth planning";
  return "Optional";
}

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  const [open, setOpen] = useState(false);
  const stage = STAGE_MAP[rec.stage];

  return (
    <article
      className={cn(
        "flex flex-col rounded-2xl border bg-card p-5 shadow-card transition-shadow hover:shadow-lift",
        stage.border,
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="font-display text-base font-semibold text-navy">{rec.name}</h3>
          <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{rec.description}</p>
        </div>
        <div className={cn("shrink-0 rounded-xl px-3 py-2 text-center", stage.bg)}>
          <div className={cn("font-display text-lg font-bold leading-none", stage.text)}>
            {rec.score}
          </div>
          <div className={cn("mt-1 text-[10px] font-medium uppercase tracking-wide", stage.text)}>
            match
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span
          className={cn("rounded-full px-2.5 py-1 text-xs font-medium", stage.bg, stage.text)}
        >
          {priority(rec.score)}
        </span>
        <span className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground">
          {stage.label}
        </span>
      </div>

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="mt-4 flex items-center gap-1.5 self-start text-sm font-medium text-primary"
      >
        Why this was recommended
        <ChevronDown className={cn("size-4 transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="mt-3 rounded-xl bg-muted/70 p-4 text-sm leading-relaxed text-foreground/85">
          {rec.reason}
        </div>
      )}

      <Link
        to="/frameworks/$slug"
        params={{ slug: rec.slug }}
        className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-navy hover:underline"
      >
        View framework detail <ArrowRight className="size-4" />
      </Link>
    </article>
  );
}
