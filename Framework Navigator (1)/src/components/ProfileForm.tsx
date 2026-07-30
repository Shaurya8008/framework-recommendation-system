import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { emptyProfile, type OrgProfile } from "@/lib/recommend";

const INDUSTRIES = [
  ["manufacturing", "Manufacturing"],
  ["energy", "Energy & utilities"],
  ["chemicals", "Chemicals & pharma"],
  ["construction", "Construction & real estate"],
  ["transport", "Transport & logistics"],
  ["agriculture", "Agriculture & food production"],
  ["consumer-goods", "Consumer goods & retail"],
  ["technology", "Technology & software"],
  ["financial", "Financial services"],
  ["services", "Professional services"],
  ["healthcare", "Healthcare"],
  ["hospitality", "Hospitality & tourism"],
];

const SIZES = [
  ["1-50", "1–50 employees"],
  ["51-250", "51–250 employees"],
  ["251-1000", "251–1,000 employees"],
  ["1000-5000", "1,000–5,000 employees"],
  ["5000+", "5,000+ employees"],
];

const REGIONS = [
  ["eu", "European Union / EEA"],
  ["uk", "United Kingdom"],
  ["india", "India"],
  ["us", "United States"],
  ["apac", "Asia Pacific (other)"],
  ["mena", "Middle East & Africa"],
  ["latam", "Latin America"],
  ["global", "Multi-region / global"],
];

const ENERGY = [
  ["low", "Low — office-based"],
  ["moderate", "Moderate — light operations"],
  ["high", "High — plants, fleets or facilities"],
  ["very-high", "Very high — energy-intensive processes"],
];

const CERTS = [
  ["iso-14001", "ISO 14001 (Environment)"],
  ["iso-50001", "ISO 50001 (Energy)"],
  ["iso-45001", "ISO 45001 (Health & safety)"],
  ["iso-9001", "ISO 9001 (Quality)"],
  ["iso-14064", "ISO 14064 (GHG verification)"],
  ["none", "None yet"],
];

const GOALS = [
  ["net-zero", "Reach net zero"],
  ["sbti", "Set science-based targets"],
  ["sdg", "Align to the UN SDGs"],
  ["renewables", "Shift to renewable energy"],
  ["compliance", "Meet regulatory requirements"],
  ["supply-chain", "Answer customer / supply-chain requests"],
  ["stakeholder-trust", "Build investor & stakeholder trust"],
  ["cost", "Reduce energy and resource cost"],
];

const MATURITY = [
  ["none", "None", "We do not track emissions today"],
  ["basic", "Basic", "Spreadsheets, partial Scope 1 & 2"],
  ["advanced", "Advanced", "Full Scope 1, 2 and material Scope 3"],
] as const;

const DISCLOSURE = [
  ["none", "None", "Nothing published externally"],
  ["partial", "Partial", "Website page or customer questionnaires"],
  ["full", "Full", "Annual public sustainability report"],
] as const;

function Section({
  step,
  title,
  description,
  children,
}: {
  step: number;
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-border bg-card p-6 shadow-card sm:p-8">
      <div className="flex items-baseline gap-3">
        <span className="font-display text-sm font-semibold text-primary">
          {String(step).padStart(2, "0")}
        </span>
        <div>
          <h2 className="text-lg font-semibold">{title}</h2>
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        </div>
      </div>
      <div className="mt-6 space-y-5">{children}</div>
    </section>
  );
}

function CheckGrid({
  options,
  values,
  onToggle,
}: {
  options: string[][];
  values: string[];
  onToggle: (v: string) => void;
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {options.map(([value, label]) => (
        <label
          key={value}
          className="flex cursor-pointer items-center gap-3 rounded-xl border border-border bg-background px-4 py-3 text-sm transition-colors hover:border-primary/40 has-[[data-state=checked]]:border-primary has-[[data-state=checked]]:bg-secondary"
        >
          <Checkbox checked={values.includes(value)} onCheckedChange={() => onToggle(value)} />
          {label}
        </label>
      ))}
    </div>
  );
}

function RadioCards({
  name,
  options,
  value,
  onChange,
}: {
  name: string;
  options: readonly (readonly [string, string, string])[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <RadioGroup value={value} onValueChange={onChange} className="grid gap-3 sm:grid-cols-3">
      {options.map(([val, label, hint]) => (
        <label
          key={val}
          className="flex cursor-pointer flex-col gap-1 rounded-xl border border-border bg-background p-4 transition-colors hover:border-primary/40 has-[[data-state=checked]]:border-primary has-[[data-state=checked]]:bg-secondary"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-navy">
            <RadioGroupItem value={val} id={`${name}-${val}`} />
            {label}
          </span>
          <span className="pl-6 text-xs text-muted-foreground">{hint}</span>
        </label>
      ))}
    </RadioGroup>
  );
}

export function ProfileForm({
  onSubmit,
  loading,
}: {
  onSubmit: (profile: OrgProfile) => void;
  loading?: boolean;
}) {
  const [profile, setProfile] = useState<OrgProfile>(emptyProfile);
  const set = <K extends keyof OrgProfile>(key: K, value: OrgProfile[K]) =>
    setProfile((p) => ({ ...p, [key]: value }));
  const toggle = (key: "certifications" | "goals", value: string) =>
    setProfile((p) => ({
      ...p,
      [key]: p[key].includes(value) ? p[key].filter((v) => v !== value) : [...p[key], value],
    }));

  const ready = profile.industry && profile.size && profile.region && profile.energyUse;

  return (
    <form
      className="space-y-5"
      onSubmit={(e) => {
        e.preventDefault();
        if (ready) onSubmit(profile);
      }}
    >
      <Section step={1} title="Organization" description="The basics we use to scope obligations.">
        <div className="grid gap-5 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="orgname">Organization name (optional)</Label>
            <Input
              id="orgname"
              maxLength={120}
              value={profile.organizationName}
              onChange={(e) => set("organizationName", e.target.value)}
              placeholder="Northwind Materials Ltd"
            />
          </div>
          <div className="space-y-2">
            <Label>Industry</Label>
            <Select value={profile.industry} onValueChange={(v) => set("industry", v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select industry" />
              </SelectTrigger>
              <SelectContent>
                {INDUSTRIES.map(([v, l]) => (
                  <SelectItem key={v} value={v}>
                    {l}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Company size</Label>
            <Select value={profile.size} onValueChange={(v) => set("size", v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select size" />
              </SelectTrigger>
              <SelectContent>
                {SIZES.map(([v, l]) => (
                  <SelectItem key={v} value={v}>
                    {l}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Primary region of operation</Label>
            <Select value={profile.region} onValueChange={(v) => set("region", v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select region" />
              </SelectTrigger>
              <SelectContent>
                {REGIONS.map(([v, l]) => (
                  <SelectItem key={v} value={v}>
                    {l}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Section>

      <Section
        step={2}
        title="Energy & emissions"
        description="How much energy you use, and how well you currently measure."
      >
        <div className="space-y-2">
          <Label>Energy use level</Label>
          <Select value={profile.energyUse} onValueChange={(v) => set("energyUse", v)}>
            <SelectTrigger className="sm:max-w-sm">
              <SelectValue placeholder="Select energy use level" />
            </SelectTrigger>
            <SelectContent>
              {ENERGY.map(([v, l]) => (
                <SelectItem key={v} value={v}>
                  {l}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-3">
          <Label>Emissions tracking maturity</Label>
          <RadioCards
            name="maturity"
            options={MATURITY}
            value={profile.emissionsMaturity}
            onChange={(v) => set("emissionsMaturity", v as OrgProfile["emissionsMaturity"])}
          />
        </div>
      </Section>

      <Section
        step={3}
        title="Certifications & disclosure"
        description="What you already hold, and what you publish today."
      >
        <div className="space-y-3">
          <Label>Existing certifications</Label>
          <CheckGrid
            options={CERTS}
            values={profile.certifications}
            onToggle={(v) => toggle("certifications", v)}
          />
        </div>
        <div className="space-y-3">
          <Label>Current disclosure practice</Label>
          <RadioCards
            name="disclosure"
            options={DISCLOSURE}
            value={profile.disclosure}
            onChange={(v) => set("disclosure", v as OrgProfile["disclosure"])}
          />
        </div>
      </Section>

      <Section
        step={4}
        title="Sustainability goals"
        description="Where you want to get to — this shapes the Improve stage."
      >
        <CheckGrid options={GOALS} values={profile.goals} onToggle={(v) => toggle("goals", v)} />
      </Section>

      <div className="flex flex-wrap items-center gap-4 pt-2">
        <Button type="submit" size="lg" disabled={!ready || loading} className="rounded-full px-7">
          {loading && <Loader2 className="size-4 animate-spin" />}
          {loading ? "Matching frameworks…" : "Get my recommendations"}
        </Button>
        {!ready && (
          <p className="text-sm text-muted-foreground">
            Industry, size, region and energy use are required.
          </p>
        )}
      </div>
    </form>
  );
}
