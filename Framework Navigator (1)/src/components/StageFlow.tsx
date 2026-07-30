import { ChevronRight } from "lucide-react";
import { STAGES, type StageId } from "@/lib/frameworks";
import { cn } from "@/lib/utils";

export function StageFlow({
  counts,
  active,
  onSelect,
}: {
  counts?: Record<StageId, number>;
  active?: StageId;
  onSelect?: (id: StageId) => void;
}) {
  return (
    <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center">
      {STAGES.map((stage, i) => {
        const Icon = stage.icon;
        const clickable = Boolean(onSelect);
        return (
          <div key={stage.id} className="flex flex-1 items-center gap-2">
            <button
              type="button"
              disabled={!clickable}
              onClick={() => onSelect?.(stage.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-xl border bg-card px-4 py-3 text-left transition-shadow",
                stage.border,
                clickable && "hover:shadow-card",
                active === stage.id && "shadow-card",
              )}
            >
              <span
                className={cn(
                  "flex size-9 shrink-0 items-center justify-center rounded-lg",
                  stage.bg,
                )}
              >
                <Icon className={cn("size-[18px]", stage.text)} />
              </span>
              <span className="min-w-0">
                <span className="block font-display text-sm font-semibold text-navy">
                  {stage.label}
                </span>
                <span className="block text-xs text-muted-foreground">
                  {counts ? `${counts[stage.id]} recommended` : stage.subtitle}
                </span>
              </span>
            </button>
            {i < STAGES.length - 1 && (
              <ChevronRight className="hidden size-4 shrink-0 text-muted-foreground sm:block" />
            )}
          </div>
        );
      })}
    </div>
  );
}
