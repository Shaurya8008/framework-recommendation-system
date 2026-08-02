import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { ProfileForm } from "@/components/ProfileForm";
import { getRecommendations, saveResult, type OrgProfile } from "@/lib/recommend";
import { toast } from "sonner";

export const Route = createFileRoute("/assess")({
  head: () => ({
    meta: [
      { title: "Organization profile — FrameworkFit assessment" },
      {
        name: "description",
        content:
          "Answer eight questions about your industry, energy use, certifications and goals to get ranked sustainability framework recommendations.",
      },
      { property: "og:title", content: "Organization profile — FrameworkFit assessment" },
      {
        property: "og:description",
        content: "Eight questions to a ranked, explainable sustainability framework roadmap.",
      },
    ],
  }),
  component: AssessPage,
});

function AssessPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  async function handleSubmit(profile: OrgProfile) {
    setLoading(true);
    try {
      const result = await getRecommendations({ data: profile });
      saveResult(profile, result);
      navigate({ to: "/results" });
    } catch {
      toast.error("We couldn't generate recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-3xl px-5 py-12">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
          Organization profile
        </p>
        <h1 className="mt-3 text-3xl font-semibold sm:text-4xl">
          Tell us about your organization
        </h1>
        <p className="mt-3 text-muted-foreground">
          Roughly two minutes. Nothing is published — your answers only drive the recommendation
          engine.
        </p>
        <div className="mt-10">
          <ProfileForm onSubmit={handleSubmit} loading={loading} />
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
