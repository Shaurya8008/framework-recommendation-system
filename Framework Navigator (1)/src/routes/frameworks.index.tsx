import { createFileRoute, Link } from "@tanstack/react-router";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { FRAMEWORKS, STAGES } from "@/lib/frameworks";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/frameworks/")({
  head: () => ({
    meta: [
      { title: "Framework library — ISO, GHG Protocol, GRI, CSRD, SBTi" },
      {
        name: "description",
        content:
          "Browse sustainability frameworks by stage: management systems, measurement standards, disclosure regimes and target-setting initiatives.",
      },
      { property: "og:title", content: "Framework library — FrameworkFit" },
      {
        property: "og:description",
        content: "Every framework we recommend, grouped by Manage, Measure, Report and Improve.",
      },
    ],
  }),
  component: FrameworkLibrary,
});

function FrameworkLibrary() {
  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-5 py-12">
        <h1 className="text-3xl font-semibold sm:text-4xl">Framework library</h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">
          Every framework in the engine, grouped by the stage it belongs to.
        </p>

        <div className="mt-12 space-y-14">
          {STAGES.map((stage) => {
            const Icon = stage.icon;
            const items = FRAMEWORKS.filter((f) => f.stage === stage.id);
            return (
              <section key={stage.id}>
                <div className="flex items-center gap-3">
                  <span
                    className={cn("flex size-10 items-center justify-center rounded-xl", stage.bg)}
                  >
                    <Icon className={cn("size-5", stage.text)} />
                  </span>
                  <div>
                    <h2 className="text-xl font-semibold">{stage.label}</h2>
                    <p className="text-sm text-muted-foreground">{stage.subtitle}</p>
                  </div>
                </div>
                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  {items.map((f) => (
                    <Link
                      key={f.slug}
                      to="/frameworks/$slug"
                      params={{ slug: f.slug }}
                      className={cn(
                        "rounded-2xl border bg-card p-5 shadow-card transition-shadow hover:shadow-lift",
                        stage.border,
                      )}
                    >
                      <h3 className="font-display text-base font-semibold text-navy">{f.name}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                        {f.summary}
                      </p>
                    </Link>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
