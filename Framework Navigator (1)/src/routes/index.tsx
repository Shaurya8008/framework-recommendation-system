import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, ShieldCheck, ListOrdered, Sparkles } from "lucide-react";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { StageFlow } from "@/components/StageFlow";
import { STAGES } from "@/lib/frameworks";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "FrameworkFit — Which sustainability frameworks apply to you?" },
      {
        name: "description",
        content:
          "Answer a short organization profile and get ranked, explainable sustainability framework recommendations across Manage, Measure, Report and Improve.",
      },
      {
        property: "og:title",
        content: "FrameworkFit — Which sustainability frameworks apply to you?",
      },
      {
        property: "og:description",
        content:
          "ISO 14001, GHG Protocol, GRI, CSRD, BRSR, ISSB, SBTi — sequenced into four clear stages for your organization.",
      },
    ],
  }),
  component: Landing,
});

const VALUE_PROPS = [
  {
    icon: ListOrdered,
    title: "Sequenced, not listed",
    body: "Frameworks arrive in the order they actually make sense: manage, then measure, then report, then improve.",
  },
  {
    icon: ShieldCheck,
    title: "Explainable by default",
    body: "Every recommendation carries a plain-language reason tied to your industry, size, region and maturity.",
  },
  {
    icon: Sparkles,
    title: "Scoped to your profile",
    body: "No generic checklist. CSRD, BRSR and SBTi appear only when your answers put them in scope.",
  },
];

function Landing() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main>
        <section className="surface-grid border-b border-border/70">
          <div className="mx-auto max-w-4xl px-5 py-20 text-center sm:py-28">
            <span className="inline-flex items-center rounded-full border border-primary/25 bg-secondary px-3.5 py-1.5 text-xs font-medium text-secondary-foreground">
              For sustainability managers, ESG consultants and founders
            </span>
            <h1 className="mt-6 text-balance text-4xl font-semibold leading-[1.1] sm:text-5xl md:text-[3.4rem]">
              Confused by sustainability frameworks? Here's the simplest way to understand them.
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
              ISO 14001, GHG Protocol, GRI, CSRD, BRSR, ISSB, TCFD, SBTi. Tell us about your
              organization and we'll return a ranked, explained roadmap across four stages.
            </p>
            <div className="mt-9 flex justify-center">
              <Link
                to="/assess"
                className="inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3.5 text-base font-medium text-primary-foreground shadow-card transition-opacity hover:opacity-90"
              >
                Get my recommendations <ArrowRight className="size-4" />
              </Link>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-16">
          <h2 className="text-center text-sm font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            The four-stage sequence
          </h2>
          <div className="mt-8">
            <StageFlow />
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-4">
            {STAGES.map((s) => (
              <div key={s.id} className={cn("rounded-2xl border bg-card p-5", s.border)}>
                <p className={cn("text-xs font-semibold uppercase tracking-[0.14em]", s.text)}>
                  {s.subtitle}
                </p>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{s.blurb}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 pb-8">
          <div className="grid gap-6 rounded-3xl border border-border bg-card p-8 shadow-card md:grid-cols-3 sm:p-10">
            {VALUE_PROPS.map(({ icon: Icon, title, body }) => (
              <div key={title}>
                <Icon className="size-5 text-primary" />
                <h3 className="mt-3 text-base font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-16">
          <div className="flex flex-col items-start justify-between gap-6 rounded-3xl bg-navy px-8 py-10 sm:flex-row sm:items-center sm:px-12">
            <div>
              <h2 className="text-2xl font-semibold text-background">
                Find your starting point in two minutes.
              </h2>
              <p className="mt-2 text-sm text-background/70">
                Eight questions. No account required.
              </p>
            </div>
            <Link
              to="/assess"
              className="inline-flex shrink-0 items-center gap-2 rounded-full bg-background px-6 py-3 text-sm font-medium text-navy transition-opacity hover:opacity-90"
            >
              Get my recommendations <ArrowRight className="size-4" />
            </Link>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
