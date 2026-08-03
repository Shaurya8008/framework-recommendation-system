import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Check, ListChecks, Users } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { STAGE_MAP, getFramework, type FrameworkInfo } from "@/lib/frameworks";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/frameworks/$slug")({
  loader: async ({ params }): Promise<{ framework: FrameworkInfo }> => {
    const framework = await getFramework({ data: params.slug });
    if (!framework) throw notFound();
    return { framework };
  },
  head: ({ loaderData }) => {
    if (!loaderData) {
      return {
        meta: [{ title: "Framework unavailable — FrameworkFit" }, { name: "robots", content: "noindex" }],
      };
    }
    const { framework } = loaderData;
    const title = `${framework.fullName} — FrameworkFit`;
    return {
      meta: [
        { title },
        { name: "description", content: framework.summary },
        { property: "og:title", content: title },
        { property: "og:description", content: framework.summary },
      ],
    };
  },
  component: FrameworkDetail,
});

function FrameworkDetail() {
  const { framework } = Route.useLoaderData() as { framework: FrameworkInfo };
  const stage = STAGE_MAP[framework.stage];
  const Icon = stage.icon;

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-3xl px-5 py-12">
        <Link
          to="/frameworks"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-navy"
        >
          <ArrowLeft className="size-4" /> Framework library
        </Link>

        <div className="mt-6 flex items-start gap-4">
          <span className={cn("flex size-12 items-center justify-center rounded-2xl", stage.bg)}>
            <Icon className={cn("size-6", stage.text)} />
          </span>
          <div>
            <p className={cn("text-xs font-semibold uppercase tracking-[0.14em]", stage.text)}>
              {stage.label} · {stage.subtitle}
            </p>
            <h1 className="mt-1.5 text-3xl font-semibold">{framework.name}</h1>
            <p className="mt-1 text-sm text-muted-foreground">{framework.fullName}</p>
          </div>
        </div>

        <section className="mt-10 rounded-2xl border border-border bg-card p-6 shadow-card sm:p-8">
          <h2 className="text-lg font-semibold">What it is</h2>
          <p className="mt-3 leading-relaxed text-foreground/85">{framework.whatItIs}</p>
        </section>

        <section className="mt-5 rounded-2xl border border-border bg-card p-6 shadow-card sm:p-8">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <Users className="size-4 text-primary" /> Who needs it
          </h2>
          <ul className="mt-4 space-y-2.5">
            {framework.whoNeedsIt.map((item) => (
              <li key={item} className="flex gap-3 text-sm leading-relaxed text-foreground/85">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-5 rounded-2xl border border-border bg-card p-6 shadow-card sm:p-8">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <ListChecks className="size-4 text-primary" /> Prerequisites
          </h2>
          <ul className="mt-4 space-y-2.5">
            {framework.prerequisites.map((item) => (
              <li key={item} className="flex gap-3 text-sm leading-relaxed text-foreground/85">
                <span className="mt-2 size-1.5 shrink-0 rounded-full bg-primary" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-5 rounded-2xl border border-border bg-muted/60 p-6 sm:p-8">
          <h2 className="text-lg font-semibold">Examples in practice</h2>
          <ul className="mt-4 space-y-3">
            {framework.examples.map((item) => (
              <li key={item} className="text-sm italic leading-relaxed text-foreground/80">
                “{item}”
              </li>
            ))}
          </ul>
        </section>

        <div className="mt-10">
          <Link
            to="/assess"
            className="inline-flex items-center rounded-full bg-primary px-6 py-3 text-sm font-medium text-primary-foreground"
          >
            Check if this applies to you
          </Link>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
