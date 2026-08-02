import { Gauge, LineChart, FileText, Target, type LucideIcon } from "lucide-react";

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

export type FrameworkInfo = {
  slug: string;
  name: string;
  fullName: string;
  stage: StageId;
  summary: string;
  whatItIs: string;
  whoNeedsIt: string[];
  prerequisites: string[];
  examples: string[];
};

export const FRAMEWORKS: FrameworkInfo[] = [
  {
    slug: "iso-14001",
    name: "ISO 14001",
    fullName: "ISO 14001 — Environmental Management Systems",
    stage: "manage",
    summary: "Certifiable management system for controlling environmental impacts.",
    whatItIs:
      "An international standard describing how to build an environmental management system (EMS): policy, aspects and impacts register, legal register, objectives, operational control, internal audit and management review. It is certifiable by an accredited third party.",
    whoNeedsIt: [
      "Manufacturing, construction and logistics organisations with site-level impacts",
      "Suppliers whose customers require certified environmental management",
      "Organisations with no formal environmental governance yet",
    ],
    prerequisites: [
      "Documented environmental policy signed by leadership",
      "Register of environmental aspects and applicable legal requirements",
      "Internal audit capability or an external auditor",
    ],
    examples: [
      "An auto-components supplier certifies three plants to win an OEM contract.",
      "A logistics firm uses ISO 14001 to structure waste and spill controls.",
    ],
  },
  {
    slug: "iso-50001",
    name: "ISO 50001",
    fullName: "ISO 50001 — Energy Management Systems",
    stage: "manage",
    summary: "Management system dedicated to continual improvement of energy performance.",
    whatItIs:
      "A standard for establishing an energy management system: energy review, baselines, energy performance indicators (EnPIs), and action plans that drive measurable consumption reduction.",
    whoNeedsIt: [
      "Energy-intensive operations (cement, steel, chemicals, data centres, cold chain)",
      "Organisations where energy is a top-three operating cost",
      "Sites subject to mandatory energy audit regimes",
    ],
    prerequisites: [
      "At least 12 months of metered energy consumption data",
      "Named energy manager or cross-functional energy team",
    ],
    examples: [
      "A textile mill cuts specific energy consumption 9% in two years under ISO 50001.",
      "A data centre pairs ISO 50001 with PUE targets for customer assurance.",
    ],
  },
  {
    slug: "iso-45001",
    name: "ISO 45001",
    fullName: "ISO 45001 — Occupational Health & Safety",
    stage: "manage",
    summary: "Health and safety management system, often paired with ISO 14001.",
    whatItIs:
      "A management system standard for occupational health and safety risk, using the same high-level structure as ISO 14001 so the two integrate cleanly into one HSE system.",
    whoNeedsIt: [
      "Operations with field, plant or contractor workforces",
      "Organisations already certified to ISO 14001 seeking an integrated HSE system",
    ],
    prerequisites: ["Incident reporting process", "Hazard identification and risk assessment"],
    examples: ["A construction group integrates 14001 + 45001 audits into a single cycle."],
  },
  {
    slug: "ghg-protocol",
    name: "GHG Protocol",
    fullName: "Greenhouse Gas Protocol — Corporate Standard",
    stage: "measure",
    summary: "The default accounting rulebook for Scope 1, 2 and 3 emissions.",
    whatItIs:
      "The globally accepted methodology for corporate greenhouse gas inventories. Defines organisational boundaries, Scope 1 (direct), Scope 2 (purchased energy) and the 15 categories of Scope 3 (value chain) emissions.",
    whoNeedsIt: [
      "Any organisation starting an emissions inventory",
      "Anyone preparing for CSRD, ISSB, BRSR, CDP or SBTi — all of which build on it",
    ],
    prerequisites: [
      "Activity data: fuel, electricity, travel, purchased goods",
      "Defined organisational and operational boundaries",
      "Emission factor source (national grid factors, DEFRA, IEA)",
    ],
    examples: [
      "A SaaS company finds 85% of its footprint in Scope 3 purchased services.",
      "A food brand maps Scope 3 category 1 to prioritise supplier engagement.",
    ],
  },
  {
    slug: "iso-14064",
    name: "ISO 14064",
    fullName: "ISO 14064 — GHG Quantification & Verification",
    stage: "measure",
    summary: "Standard for quantifying and independently verifying GHG inventories.",
    whatItIs:
      "A three-part standard covering organisation-level GHG inventories (Part 1), project-level reductions (Part 2) and validation/verification (Part 3). Used when an inventory needs assurance.",
    whoNeedsIt: [
      "Organisations needing third-party assurance on emissions numbers",
      "Companies whose disclosures face limited or reasonable assurance requirements",
    ],
    prerequisites: ["An existing GHG inventory, typically built to the GHG Protocol"],
    examples: ["A listed company verifies its Scope 1 and 2 data ahead of assured reporting."],
  },
  {
    slug: "lca-iso-14040",
    name: "LCA (ISO 14040/44)",
    fullName: "Life Cycle Assessment — ISO 14040 / 14044",
    stage: "measure",
    summary: "Product-level environmental footprint across the full life cycle.",
    whatItIs:
      "A methodology for assessing impacts of a product or service from raw material extraction through end of life, producing results used in EPDs and product carbon footprints.",
    whoNeedsIt: [
      "Product manufacturers facing customer or retailer footprint requests",
      "Companies making product-level environmental claims",
    ],
    prerequisites: ["Bill of materials and process data", "Defined functional unit and boundaries"],
    examples: ["A packaging producer publishes EPDs for its top five SKUs."],
  },
  {
    slug: "gri",
    name: "GRI Standards",
    fullName: "Global Reporting Initiative Standards",
    stage: "report",
    summary: "Multi-stakeholder sustainability reporting standard used worldwide.",
    whatItIs:
      "A modular reporting standard (universal, sector and topic standards) built on impact materiality — reporting the organisation's effects on economy, environment and people.",
    whoNeedsIt: [
      "Organisations publishing a voluntary sustainability report",
      "Companies with broad stakeholder audiences beyond investors",
    ],
    prerequisites: ["Materiality assessment", "Reliable topic-level data for a full year"],
    examples: ["A mid-size manufacturer publishes its first GRI-referenced report."],
  },
  {
    slug: "issb",
    name: "ISSB (IFRS S1/S2)",
    fullName: "ISSB — IFRS S1 & S2 Sustainability Disclosure Standards",
    stage: "report",
    summary: "Investor-focused global baseline for sustainability and climate disclosure.",
    whatItIs:
      "IFRS S1 covers general sustainability-related financial disclosures; IFRS S2 covers climate, absorbing the TCFD structure of governance, strategy, risk management, and metrics and targets.",
    whoNeedsIt: [
      "Listed companies and those in jurisdictions adopting ISSB",
      "Organisations answering investor climate-risk questions",
    ],
    prerequisites: ["Scope 1 and 2 inventory", "Climate risk and scenario analysis"],
    examples: ["A listed group aligns its annual report climate section to IFRS S2."],
  },
  {
    slug: "csrd",
    name: "CSRD / ESRS",
    fullName: "Corporate Sustainability Reporting Directive (ESRS)",
    stage: "report",
    summary: "Mandatory, assured EU reporting under the ESRS with double materiality.",
    whatItIs:
      "EU legislation requiring in-scope companies to report against the European Sustainability Reporting Standards, with double materiality assessment, digital tagging and third-party assurance.",
    whoNeedsIt: [
      "Large EU companies and EU-listed entities",
      "Non-EU groups with significant EU turnover and subsidiaries",
    ],
    prerequisites: [
      "Double materiality assessment",
      "Value-chain data collection process",
      "Audit-ready internal controls over sustainability data",
    ],
    examples: ["A non-EU manufacturer prepares ESRS data for its European subsidiary."],
  },
  {
    slug: "brsr",
    name: "BRSR",
    fullName: "Business Responsibility & Sustainability Report (India)",
    stage: "report",
    summary: "SEBI-mandated ESG disclosure format for large listed Indian companies.",
    whatItIs:
      "A prescribed disclosure format structured around the nine NGRBC principles, with essential and leadership indicators, plus BRSR Core attributes subject to reasonable assurance.",
    whoNeedsIt: [
      "Top-listed companies on Indian exchanges",
      "Value-chain partners of listed Indian companies",
    ],
    prerequisites: ["Energy, water, waste and emissions data", "Workforce and social metrics"],
    examples: ["An Indian listed manufacturer files BRSR Core with assured intensity ratios."],
  },
  {
    slug: "tcfd",
    name: "TCFD",
    fullName: "Task Force on Climate-related Financial Disclosures",
    stage: "report",
    summary: "Climate risk disclosure structure now carried forward inside IFRS S2.",
    whatItIs:
      "A four-pillar framework — governance, strategy, risk management, metrics and targets — for disclosing climate-related financial risks and opportunities, including scenario analysis.",
    whoNeedsIt: [
      "Companies answering lender or investor climate risk questionnaires",
      "Organisations transitioning toward ISSB reporting",
    ],
    prerequisites: ["Board oversight of climate", "Climate scenario analysis"],
    examples: ["A logistics group runs 1.5°C and 3°C scenarios on its port assets."],
  },
  {
    slug: "cdp",
    name: "CDP",
    fullName: "CDP Disclosure (Climate, Water, Forests)",
    stage: "report",
    summary: "Questionnaire-based disclosure often requested by customers and investors.",
    whatItIs:
      "An annual scored questionnaire covering climate change, water security and forests, widely used by procurement teams and investors to benchmark suppliers.",
    whoNeedsIt: [
      "Suppliers to large corporates that cascade CDP requests",
      "Companies wanting an external benchmark score",
    ],
    prerequisites: ["Scope 1, 2 and material Scope 3 data", "Targets and governance detail"],
    examples: ["A component supplier lifts its CDP score from D to B in two cycles."],
  },
  {
    slug: "sbti",
    name: "SBTi",
    fullName: "Science Based Targets initiative",
    stage: "improve",
    summary: "Validated emissions targets aligned to 1.5°C pathways.",
    whatItIs:
      "A target-setting and validation process. Companies submit near-term (and optionally net-zero) targets, which are checked against sector pathways and published once approved.",
    whoNeedsIt: [
      "Companies committing publicly to net zero",
      "Suppliers whose customers require validated targets",
    ],
    prerequisites: [
      "A complete base-year Scope 1, 2 and screened Scope 3 inventory",
      "Executive sign-off on a reduction trajectory",
    ],
    examples: ["A retailer validates a 42% absolute Scope 1+2 cut by 2030 from a 2022 base."],
  },
  {
    slug: "net-zero-standard",
    name: "Net-Zero Standard",
    fullName: "Corporate Net-Zero Standard",
    stage: "improve",
    summary: "Rules for what a credible corporate net-zero claim requires.",
    whatItIs:
      "Defines long-term deep decarbonisation (typically ~90%) before any neutralisation of residual emissions, plus interim near-term targets and beyond-value-chain mitigation guidance.",
    whoNeedsIt: [
      "Organisations that have already published a net-zero ambition",
      "Companies needing to defend claims against greenwashing scrutiny",
    ],
    prerequisites: ["Validated near-term science-based targets", "Scope 3 reduction plan"],
    examples: ["A consumer brand replaces a vague 2050 pledge with a validated pathway."],
  },
  {
    slug: "sdgs",
    name: "UN SDGs",
    fullName: "United Nations Sustainable Development Goals",
    stage: "improve",
    summary: "A shared 17-goal language for framing sustainability strategy and impact.",
    whatItIs:
      "Seventeen global goals with 169 targets. Companies map material activities to specific SDG targets and indicators rather than claiming whole goals.",
    whoNeedsIt: [
      "Organisations communicating purpose to employees, customers and communities",
      "Companies working with development finance or public sector buyers",
    ],
    prerequisites: ["Materiality view of where the business genuinely contributes"],
    examples: ["A services firm maps its programmes to SDG 7, 12 and 13 targets."],
  },
  {
    slug: "renewable-energy-plan",
    name: "Renewable Energy Roadmap",
    fullName: "Renewable Energy Sourcing Roadmap (RE100-style)",
    stage: "improve",
    summary: "A staged plan to shift purchased electricity to renewable sources.",
    whatItIs:
      "A commitment and plan to source electricity from renewables through on-site generation, PPAs or attribute certificates, with milestones and a claims methodology.",
    whoNeedsIt: [
      "Electricity-intensive operations with large Scope 2 footprints",
      "Companies with Scope 2 reduction targets",
    ],
    prerequisites: ["Site-level electricity consumption data", "Market-based Scope 2 accounting"],
    examples: ["A campus signs a solar PPA covering 60% of annual load."],
  },
];

export const FRAMEWORK_MAP: Record<string, FrameworkInfo> = Object.fromEntries(
  FRAMEWORKS.map((f) => [f.slug, f]),
);
