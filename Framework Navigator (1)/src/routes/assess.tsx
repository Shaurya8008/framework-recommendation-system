import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { SiteHeader, SiteFooter } from "@/components/SiteChrome";
import { ProfileForm } from "@/components/ProfileForm";
import { getRecommendations, saveResult, type OrgProfile, DocumentUploadResponse } from "@/lib/recommend";
import { toast } from "sonner";
import { AutofillUpload } from "@/components/AutofillUpload";
import { AutofillReview } from "@/components/AutofillReview";
import { Button } from "@/components/ui/button";

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
  const [mode, setMode] = useState<"choice" | "upload" | "review" | "manual">("choice");
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [initialProfile, setInitialProfile] = useState<OrgProfile | undefined>(undefined);

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

  const handleUploadComplete = (data: DocumentUploadResponse) => {
    setUploadResult(data);
    setMode("review");
  };

  const handleApplyAutofill = (profile: OrgProfile) => {
    setInitialProfile(profile);
    setMode("manual");
  };

  return (
    <div className="min-h-screen">
      <SiteHeader />
      <main className="mx-auto max-w-3xl px-5 py-12">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">
            Organization profile
          </p>
          {mode !== "choice" && (
            <Button variant="ghost" size="sm" onClick={() => setMode("choice")}>
              &larr; Start over
            </Button>
          )}
        </div>
        
        <h1 className="mt-3 text-3xl font-semibold sm:text-4xl">
          Tell us about your organization
        </h1>
        <p className="mt-3 text-muted-foreground">
          Roughly two minutes. Nothing is published — your answers only drive the recommendation
          engine.
        </p>

        <div className="mt-10">
          {mode === "choice" && (
            <div className="grid gap-6 sm:grid-cols-2">
              <div 
                className="flex cursor-pointer flex-col justify-between rounded-2xl border border-border bg-card p-8 shadow-sm transition-colors hover:border-primary/50 hover:bg-secondary/20"
                onClick={() => setMode("upload")}
              >
                <div>
                  <h3 className="text-xl font-semibold">Upload Document</h3>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Upload a sustainability report (PDF) to automatically extract your profile details.
                  </p>
                </div>
                <Button className="mt-8 self-start" variant="secondary">Upload PDF</Button>
              </div>

              <div 
                className="flex cursor-pointer flex-col justify-between rounded-2xl border border-border bg-card p-8 shadow-sm transition-colors hover:border-primary/50 hover:bg-secondary/20"
                onClick={() => setMode("manual")}
              >
                <div>
                  <h3 className="text-xl font-semibold">Fill Manually</h3>
                  <p className="mt-3 text-sm text-muted-foreground">
                    Answer 8 quick questions to get your personalized framework recommendations.
                  </p>
                </div>
                <Button className="mt-8 self-start" variant="outline">Start questions</Button>
              </div>
            </div>
          )}

          {mode === "upload" && (
            <AutofillUpload onUploadComplete={handleUploadComplete} />
          )}

          {mode === "review" && uploadResult && (
            <AutofillReview data={uploadResult} onApply={handleApplyAutofill} />
          )}

          {mode === "manual" && (
            <ProfileForm onSubmit={handleSubmit} loading={loading} initialProfile={initialProfile} />
          )}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
