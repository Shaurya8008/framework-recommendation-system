import { Gauge, LineChart, FileText, Target, type LucideIcon } from "lucide-react";
import { createServerFn } from "@tanstack/react-start";

export type StageId = "manage" | "measure" | "report" | "improve";

export type Stage = {
  id: StageId;
  label: string;
  subtitle: string;
  blurb: string;
  icon: LucideIcon;
  /** Tailwind classes built from stage design tokens. */
  text: string;
  bg: string;
  border: string;
  dot: string;
};

export const STAGES: Stage[] = [
  {
    id: "manage",
    label: "Manage",
    subtitle: "Foundation",
    blurb: "Put management systems in place so sustainability work is repeatable and audited.",
    icon: Gauge,
    text: "text-manage",
    bg: "bg-manage-soft",
    border: "border-manage/30",
    dot: "bg-manage",
  },
  {
    id: "measure",
    label: "Measure",
    subtitle: "Measurement",
    blurb: "Quantify emissions, energy and impacts with methods auditors recognise.",
    icon: LineChart,
    text: "text-measure",
    bg: "bg-measure-soft",
    border: "border-measure/30",
    dot: "bg-measure",
  },
  {
    id: "report",
    label: "Report",
    subtitle: "Disclosure",
    blurb: "Communicate performance to regulators, investors and customers.",
    icon: FileText,
    text: "text-report",
    bg: "bg-report-soft",
    border: "border-report/30",
    dot: "bg-report",
  },
  {
    id: "improve",
    label: "Improve",
    subtitle: "Direction",
    blurb: "Set targets and a credible trajectory for reducing impact over time.",
    icon: Target,
    text: "text-improve",
    bg: "bg-improve-soft",
    border: "border-improve/30",
    dot: "bg-improve",
  },
];

export const STAGE_MAP: Record<StageId, Stage> = Object.fromEntries(
  STAGES.map((s) => [s.id, s]),
) as Record<StageId, Stage>;

// Matched with backend FrameworkRead schema
export type FrameworkInfo = {
  id: number;
  slug: string;
  name: string;
  short_name?: string;
  full_name: string;
  stage: StageId;
  topic?: string;
  subtopic?: string;
  description: string;
  what_it_is?: string;
  who_needs_it: string[];
  geography_applicability: string[];
  industry_fit: string[];
  org_size_fit: string[];
  mandatory_status: string;
  certifiable: boolean;
  output_type?: string;
  prerequisites: string[];
  data_requirements: string[];
  maturity_min: string;
  maturity_max?: string;
  implementation_effort: string;
  assurance_relevance: string;
  depends_on: string[];
  recommended_next: string[];
  priority_weight: number;
  recommendation_rule_notes?: string;
  why_recommended_template?: string;
  active: boolean;
  region_applicability: string[];
  // Fallbacks for frontend compatibility
  summary?: string;
  fullName?: string;
  whatItIs?: string;
  whoNeedsIt?: string[];
  examples?: string[];
};

const API_ENDPOINT = import.meta.env.VITE_RECOMMEND_API || process.env.VITE_RECOMMEND_API || "http://localhost:8000";

const getBaseUrl = () => {
  let endpoint = API_ENDPOINT;
  if (endpoint && !endpoint.startsWith("http")) {
    endpoint = `http://${endpoint}`;
  }
  // Strip trailing slashes or /recommend if inherited
  endpoint = endpoint.replace(/\/recommend\/?$/, "").replace(/\/$/, "");
  return endpoint;
};

export const getFrameworks = createServerFn({ method: "GET" })
  .handler(async () => {
    try {
      const endpoint = `${getBaseUrl()}/frameworks`;
      const res = await fetch(endpoint, {
        signal: AbortSignal.timeout(8000),
      });
      if (res.ok) {
        const data = await res.json() as FrameworkInfo[];
        return data.map(f => ({
          ...f,
          summary: f.description,
          fullName: f.full_name,
          whatItIs: f.what_it_is || f.description,
          whoNeedsIt: f.who_needs_it || [],
          examples: []
        }));
      }
      console.warn(`[Frameworks] Backend request to ${endpoint} returned ${res.status}. Returning empty.`);
      return [];
    } catch (err) {
      console.warn(`[Frameworks] Backend request failed (${String(err)}). Returning empty.`);
      return [];
    }
  });

export const getFramework = createServerFn({ method: "GET" })
  .validator((slug: string) => slug)
  .handler(async ({ data: slug }) => {
    try {
      const endpoint = `${getBaseUrl()}/frameworks/${slug}`;
      const res = await fetch(endpoint, {
        signal: AbortSignal.timeout(8000),
      });
      if (res.ok) {
        const f = await res.json() as FrameworkInfo;
        return {
          ...f,
          summary: f.description,
          fullName: f.full_name,
          whatItIs: f.what_it_is || f.description,
          whoNeedsIt: f.who_needs_it || [],
          examples: []
        };
      }
      console.warn(`[Framework] Backend request to ${endpoint} returned ${res.status}.`);
      return null;
    } catch (err) {
      console.warn(`[Framework] Backend request failed (${String(err)}).`);
      return null;
    }
  });

