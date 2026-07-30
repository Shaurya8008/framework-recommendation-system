import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowRight, RotateCcw } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { StageFlow } from "@/components/StageFlow";
import { StageSection } from "@/components/StageSection";
import { STAGES, type StageId } from "@/lib/frameworks";
import { loadResult, type OrgProfile, type RecommendResponse } from "@/lib/recommend";

export const Route = createFileRoute("/results")({
  head: () => ({
    meta: [
      { title: "Your framework roadmap — FrameworkFit" },
      {
        name: "description",
        content:
          "Ranked sustainability frameworks for your organization, grouped into Manage, Measure, Report and Improve, each with a reason.",
      },
      { property: "og:title", content: "Your framework roadmap — FrameworkFit" },
      {
        property: "og:description",
        content: "Ranked, explainable sustainability framework recommendations for your profile.",
      },
    ],
  }),
  component: ResultsPage,
});

function ResultsPage() {
  const [data, setData] = useState<{ profile: OrgProfile; result: RecommendResponse } | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setData(loadResult());
    setReady(true);
  }, []);

  if (!ready) return <div className="min-h-screen" />;

  if (!data) {
    return (
      <div className="min-h-screen">
        <SiteHeader />
        <main className="mx-auto max-w-2xl px-5 py-24 text-center">
          <h1 className="text-3xl font-semibold">No results yet</h1>
          <p className="mt-3 text-muted-foreground">
            Complete the organization profile to see your framework roadmap.
          </p>
          <Link
            to="/assess"
            className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-medium text-primary-foreground"
          >
            Start assessment <ArrowRight className="size-4" />
          </Link>
        </main>
        <SiteFooter />
      </div>
    );
  }

  const { result } = data;
  const counts = Object.fromEntries(
    STAGES.map((s) => [s.id, result.stages[s.id].length]),
  ) as Record<StageId, number>;
  const total = Object.values(counts).reduce((a, b) => a + b, 0);
  const topPick = STAGES.flatMap((s) => result.stages[s.id]).sort((a, b) => b.score - a.score)[0];

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-5 py-12">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
              Recommendation dashboard
            </p>
            <h1 className="mt-3 text-3xl font-semibold sm:text-4xl">Your framework roadmap</h1>
            <p className="mt-3 text-muted-foreground">
              {result.profileSummary} — {total} frameworks matched
              {topPick ? `, starting with ${topPick.name}.` : "."}
            </p>
          </div>
          <Link
            to="/assess"
            className="inline-flex items-center gap-2 rounded-full border border-border px-5 py-2.5 text-sm font-medium text-navy transition-colors hover:bg-muted"
          >
            <RotateCcw className="size-4" /> Redo assessment
          </Link>
        </div>

        <div className="mt-8">
          <StageFlow
            counts={counts}
            onSelect={(id) =>
              document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" })
            }
          />
        </div>

        <div className="mt-14 space-y-16">
          {STAGES.map((stage, i) => (
            <StageSection
              key={stage.id}
              stageId={stage.id}
              index={i}
              recommendations={result.stages[stage.id]}
            />
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
