import { type StageId, getFrameworks } from "./frameworks";
import { createServerFn } from "@tanstack/react-start";

/**
 * Swap to the real backend by setting VITE_RECOMMEND_API to the endpoint URL.
 * The mock below mirrors the exact response shape of POST /recommend.
 */
const RECOMMEND_ENDPOINT = import.meta.env.VITE_RECOMMEND_API ?? "";

export type OrgProfile = {
  organizationName: string;
  industry: string;
  size: string;
  region: string;
  energyUse: string;
  emissionsMaturity: "none" | "basic" | "advanced";
  certifications: string[];
  disclosure: "none" | "partial" | "full";
  goals: string[];
};

export type Recommendation = {
  slug: string;
  name: string;
  stage: StageId;
  description: string;
  score: number;
  reason: string;
};

export type RecommendResponse = {
  profileSummary: string;
  stages: Record<StageId, Recommendation[]>;
};

export const emptyProfile: OrgProfile = {
  organizationName: "",
  industry: "",
  size: "",
  region: "",
  energyUse: "",
  emissionsMaturity: "none",
  certifications: [],
  disclosure: "none",
  goals: [],
};

export const getRecommendations = createServerFn({ method: "POST" })
  .validator((d: OrgProfile) => d)
  .handler(async ({ data: profile }) => {
    const p = profile || emptyProfile;
    try {
      let endpoint = process.env.VITE_RECOMMEND_API || RECOMMEND_ENDPOINT || "http://localhost:8000/recommend";
      
      if (endpoint && !endpoint.startsWith("http")) {
        endpoint = `http://${endpoint}`;
      }
      if (endpoint && !endpoint.endsWith("/recommend")) {
        endpoint = endpoint.replace(/\/$/, "");
        endpoint = `${endpoint}/recommend`;
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(p),
        signal: AbortSignal.timeout(8000),
      });
      if (res.ok) {
        return (await res.json()) as RecommendResponse;
      }
      console.warn(`[Recommend] Backend request to ${endpoint} returned ${res.status}. Using fallback scoring engine.`);
      return await mockRecommend(p);
    } catch (err) {
      console.warn(`[Recommend] Backend request failed (${String(err)}). Using fallback scoring engine.`);
      return await mockRecommend(p);
    }
  });

/* ---------------- mock scoring engine ---------------- */

const HEAVY_INDUSTRIES = ["manufacturing", "energy", "chemicals", "construction", "transport"];

async function mockRecommend(p: OrgProfile): Promise<RecommendResponse> {
  const FRAMEWORKS = await getFrameworks();
  const certified = (slug: string) => p.certifications.includes(slug);
  const goal = (g: string) => p.goals.includes(g);
  const heavy = HEAVY_INDUSTRIES.includes(p.industry);
  const highEnergy = p.energyUse === "high" || p.energyUse === "very-high";
  const large = p.size === "1000-5000" || p.size === "5000+";
  const eu = p.region === "eu";
  const india = p.region === "india";

  const scored: Recommendation[] = [];
  const add = (slug: string, score: number, reason: string) => {
    const f = FRAMEWORKS.find((x) => x.slug === slug);
    if (!f) return;
    scored.push({
      slug: f.slug,
      name: f.name,
      stage: f.stage,
      description: f.summary || f.description,
      score: Math.max(10, Math.min(99, Math.round(score))),
      reason,
    });
  };

  // MANAGE
  if (!certified("iso-14001")) {
    add(
      "iso-14001",
      60 + (heavy ? 25 : 8) + (large ? 6 : 0),
      `You have no ISO 14001 certification yet${heavy ? ` and ${p.industry} operations carry site-level environmental impacts` : ""}. An EMS gives you the governance backbone every later framework assumes.`,
    );
  }
  if (!certified("iso-50001") && highEnergy) {
    add(
      "iso-50001",
      72 + (heavy ? 12 : 0),
      `You reported ${p.energyUse.replace("-", " ")} energy use, so energy is a material cost and emissions driver. ISO 50001 turns that into measured, managed reduction.`,
    );
  }
  if (!certified("iso-45001") && heavy) {
    add(
      "iso-45001",
      52,
      "Operational, plant-based work usually means occupational risk. ISO 45001 shares its structure with ISO 14001, so audits can be integrated.",
    );
  }

  // MEASURE
  add(
    "ghg-protocol-corporate",
    p.emissionsMaturity === "none" ? 96 : p.emissionsMaturity === "basic" ? 88 : 70,
    p.emissionsMaturity === "none"
      ? "You are not tracking emissions yet. The GHG Protocol is the starting point — every reporting and target framework you selected depends on this inventory."
      : p.emissionsMaturity === "basic"
        ? "Your tracking is basic. Extending to full Scope 3 coverage under the GHG Protocol unlocks disclosure and target setting."
        : "Your inventory is advanced; keep it aligned to the GHG Protocol as your reference methodology for all disclosures.",
  );
  if (p.emissionsMaturity !== "none" && (large || p.disclosure !== "none")) {
    add(
      "iso-14064-1",
      64 + (large ? 10 : 0),
      `With ${p.disclosure === "none" ? "an established inventory" : "public disclosure in play"}, third-party verification protects your numbers under scrutiny and assurance requirements.`,
    );
  }
  if (heavy || p.industry === "consumer-goods" || p.industry === "agriculture") {
    add(
      "iso-14040",
      58,
      `${p.industry.replace("-", " ")} companies face product-level footprint requests from customers and retailers; LCA is the accepted method.`,
    );
  }

  // REPORT
  if (eu || large) {
    add(
      "csrd",
      eu ? 92 : 62,
      eu
        ? "Your EU footprint puts CSRD/ESRS in scope or near-scope. It is mandatory, assured, and requires double materiality — the longest lead time of anything here."
        : "At your size, CSRD can reach you indirectly through EU customers and subsidiaries. Early ESRS gap analysis is cheap insurance.",
    );
  }
  if (india) {
    add(
      "brsr",
      90,
      "For Indian entities, BRSR is the SEBI-prescribed format and BRSR Core attributes require reasonable assurance — align your data collection to it first.",
    );
  }
  add(
    "ifrs-s1",
    large ? 82 : 58,
    large
      ? "Investor-facing entities of your size are the primary audience for IFRS S1/S2, which is becoming the global disclosure baseline."
      : "ISSB is worth tracking now so your data structure does not need rebuilding when it applies to you.",
  );
  add(
    "tcfd",
    p.disclosure === "none" ? 68 : 74,
    "TCFD's four pillars are the simplest on-ramp to climate risk disclosure and map directly into IFRS S2 later.",
  );
  if (p.disclosure !== "none" || goal("stakeholder-trust")) {
    add(
      "gri",
      p.disclosure === "full" ? 78 : 66,
      `You already report ${p.disclosure === "full" ? "publicly and fully" : "partially"}, so GRI gives that report a recognised, impact-materiality structure.`,
    );
  }
  if (large || p.disclosure === "full") {
    add(
      "cdp-climate",
      60,
      "Large buyers and investors commonly cascade CDP questionnaires; a scored response is often a procurement prerequisite.",
    );
  }

  // IMPROVE
  if (goal("net-zero") || goal("sbti")) {
    add(
      "sbti",
      94,
      "You selected science-based / net-zero ambitions. SBTi validation is what turns that ambition into a defensible, externally checked target.",
    );
    add(
      "net-zero-standard",
      80,
      "A net-zero claim needs ~90% deep decarbonisation before neutralisation. This standard defines what you must be able to evidence.",
    );
  }
  if (goal("sdg")) {
    add(
      "sdgs",
      70,
      "You want SDG alignment. Map material activities to specific SDG targets and indicators rather than claiming whole goals.",
    );
  }
  if (goal("renewables") || highEnergy) {
    add(
      "re100",
      highEnergy ? 76 : 62,
      highEnergy
        ? "High electricity consumption means Scope 2 is likely your fastest reduction lever — a sourcing roadmap converts it into a plan."
        : "You flagged renewable sourcing as a goal; a staged PPA and certificate roadmap makes it auditable.",
    );
  }

  const stages: Record<StageId, Recommendation[]> = {
    manage: [],
    measure: [],
    report: [],
    improve: [],
  };
  for (const r of scored) stages[r.stage].push(r);
  for (const k of Object.keys(stages) as StageId[]) stages[k].sort((a, b) => b.score - a.score);

  const summary = [
    p.organizationName || "Your organization",
    p.industry ? `· ${p.industry.replace("-", " ")}` : "",
    p.size ? `· ${p.size} employees` : "",
    p.region ? `· ${p.region.toUpperCase()}` : "",
  ]
    .filter(Boolean)
    .join(" ");

  return { profileSummary: summary, stages };
}

/* --------------- session persistence --------------- */

const KEY = "frameworkfit:last-result";

export function saveResult(profile: OrgProfile, result: RecommendResponse) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify({ profile, result }));
  } catch {
    /* ignore */
  }
}

export function loadResult(): { profile: OrgProfile; result: RecommendResponse } | null {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/* --------------- autofill API --------------- */

export type AutofillFieldSuggestion = {
  field: string;
  suggested_value: any;
  confidence: number;
  source: string;
  source_snippet?: string;
  reason?: string;
};

export type DocumentUploadResponse = {
  document_id: number;
  status: string;
  overall_confidence: number;
  suggestions: AutofillFieldSuggestion[];
  missing_fields: string[];
};

export const uploadDocumentForAutofill = createServerFn({ method: "POST" })
  .validator((d: { fileName: string; fileBase64: string }) => d)
  .handler(async ({ data }) => {
    let endpoint = process.env.VITE_RECOMMEND_API || "http://localhost:8000";
    if (endpoint && !endpoint.startsWith("http")) endpoint = `http://${endpoint}`;
    if (endpoint && endpoint.endsWith("/recommend")) endpoint = endpoint.replace("/recommend", "");
    if (endpoint && endpoint.endsWith("/")) endpoint = endpoint.slice(0, -1);

    // Reconstruct file from base64 on the server side
    const binaryStr = atob(data.fileBase64);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i);
    }
    const blob = new Blob([bytes], { type: "application/pdf" });

    const formData = new FormData();
    formData.append("file", blob, data.fileName);

    const res = await fetch(`${endpoint}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Upload failed (${res.status}): ${errorText}`);
    }

    return (await res.json()) as DocumentUploadResponse;
  });

