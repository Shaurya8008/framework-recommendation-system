import type { Recommendation } from "@/lib/recommend";
import { STAGE_MAP, type StageId } from "@/lib/frameworks";
import { RecommendationCard } from "./RecommendationCard";
import { cn } from "@/lib/utils";

export function StageSection({
  stageId,
  index,
  recommendations,
}: {
  stageId: StageId;
  index: number;
  recommendations: Recommendation[];
}) {
  const stage = STAGE_MAP[stageId];
  const Icon = stage.icon;

  return (
    <section id={stageId} className="scroll-mt-24">
      <div className="flex items-start gap-4">
        <span className={cn("flex size-12 items-center justify-center rounded-2xl", stage.bg)}>
          <Icon className={cn("size-6", stage.text)} />
        </span>
        <div>
          <p
            className={cn(
              "text-xs font-semibold uppercase tracking-[0.14em]",
              stage.text,
            )}
          >
            Stage {index + 1} · {stage.subtitle}
          </p>
          <h2 className="mt-1 text-2xl font-semibold">{stage.label}</h2>
          <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{stage.blurb}</p>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {recommendations.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-border p-6 text-sm text-muted-foreground">
            Nothing required at this stage based on your profile.
          </p>
        ) : (
          recommendations.map((r) => <RecommendationCard key={r.slug} rec={r} />)
        )}
      </div>
    </section>
  );
}
