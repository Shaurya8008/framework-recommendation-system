from sqlalchemy.orm import Session
from app.db.models import Framework

INITIAL_FRAMEWORKS = [
    {
        "slug": "iso-14001",
        "name": "ISO 14001",
        "full_name": "ISO 14001 — Environmental Management Systems",
        "stage": "manage",
        "description": "Certifiable management system for controlling environmental impacts.",
        "what_it_is": "An international standard describing how to build an environmental management system (EMS): policy, aspects and impacts register, legal register, objectives, operational control, internal audit and management review.",
        "who_needs_it": [
            "Manufacturing, construction and logistics organisations with site-level impacts",
            "Suppliers whose customers require certified environmental management",
            "Organisations with no formal environmental governance yet"
        ],
        "prerequisites": [
            "Documented environmental policy signed by leadership",
            "Register of environmental aspects and applicable legal requirements",
            "Internal audit capability or an external auditor"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "iso-50001",
        "name": "ISO 50001",
        "full_name": "ISO 50001 — Energy Management Systems",
        "stage": "manage",
        "description": "Management system dedicated to continual improvement of energy performance.",
        "what_it_is": "A standard for establishing an energy management system: energy review, baselines, energy performance indicators (EnPIs), and action plans that drive measurable consumption reduction.",
        "who_needs_it": [
            "Energy-intensive operations (cement, steel, chemicals, data centres, cold chain)",
            "Organisations where energy is a top-three operating cost",
            "Sites subject to mandatory energy audit regimes"
        ],
        "prerequisites": [
            "At least 12 months of metered energy consumption data",
            "Named energy manager or cross-functional energy team"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "iso-45001",
        "name": "ISO 45001",
        "full_name": "ISO 45001 — Occupational Health & Safety",
        "stage": "manage",
        "description": "Health and safety management system, often paired with ISO 14001.",
        "what_it_is": "A management system standard for occupational health and safety risk, using the same high-level structure as ISO 14001 so the two integrate cleanly into one HSE system.",
        "who_needs_it": [
            "Operations with field, plant or contractor workforces",
            "Organisations already certified to ISO 14001 seeking an integrated HSE system"
        ],
        "prerequisites": [
            "Incident reporting process",
            "Hazard identification and risk assessment"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "ghg-protocol",
        "name": "GHG Protocol",
        "full_name": "Greenhouse Gas Protocol — Corporate Standard",
        "stage": "measure",
        "description": "The default accounting rulebook for Scope 1, 2 and 3 emissions.",
        "what_it_is": "The globally accepted methodology for corporate greenhouse gas inventories. Defines organisational boundaries, Scope 1 (direct), Scope 2 (purchased energy) and the 15 categories of Scope 3 (value chain) emissions.",
        "who_needs_it": [
            "Any organisation starting an emissions inventory",
            "Anyone preparing for CSRD, ISSB, BRSR, CDP or SBTi — all of which build on it"
        ],
        "prerequisites": [
            "Activity data: fuel, electricity, travel, purchased goods",
            "Defined organisational and operational boundaries",
            "Emission factor source (national grid factors, DEFRA, IEA)"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "iso-14064",
        "name": "ISO 14064",
        "full_name": "ISO 14064 — GHG Quantification & Verification",
        "stage": "measure",
        "description": "Standard for quantifying and independently verifying GHG inventories.",
        "what_it_is": "A three-part standard covering organisation-level GHG inventories (Part 1), project-level reductions (Part 2) and validation/verification (Part 3). Used when an inventory needs assurance.",
        "who_needs_it": [
            "Organisations needing third-party assurance on emissions numbers",
            "Companies whose disclosures face limited or reasonable assurance requirements"
        ],
        "prerequisites": [
            "An existing GHG inventory, typically built to the GHG Protocol"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "lca-iso-14040",
        "name": "LCA (ISO 14040/44)",
        "full_name": "Life Cycle Assessment — ISO 14040 / 14044",
        "stage": "measure",
        "description": "Product-level environmental footprint across the full life cycle.",
        "what_it_is": "A methodology for assessing impacts of a product or service from raw material extraction through end of life, producing results used in EPDs and product carbon footprints.",
        "who_needs_it": [
            "Product manufacturers facing customer or retailer footprint requests",
            "Companies making product-level environmental claims"
        ],
        "prerequisites": [
            "Bill of materials and process data",
            "Defined functional unit and boundaries"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "gri",
        "name": "GRI Standards",
        "full_name": "Global Reporting Initiative Standards",
        "stage": "report",
        "description": "Multi-stakeholder sustainability reporting standard used worldwide.",
        "what_it_is": "A modular reporting standard (universal, sector and topic standards) built on impact materiality — reporting the organisation's effects on economy, environment and people.",
        "who_needs_it": [
            "Organisations publishing a voluntary sustainability report",
            "Companies with broad stakeholder audiences beyond investors"
        ],
        "prerequisites": [
            "Materiality assessment",
            "Reliable topic-level data for a full year"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "issb",
        "name": "ISSB (IFRS S1/S2)",
        "full_name": "ISSB — IFRS S1 & S2 Sustainability Disclosure Standards",
        "stage": "report",
        "description": "Investor-focused global baseline for sustainability and climate disclosure.",
        "what_it_is": "IFRS S1 covers general sustainability-related financial disclosures; IFRS S2 covers climate, absorbing the TCFD structure of governance, strategy, risk management, and metrics and targets.",
        "who_needs_it": [
            "Listed companies and those in jurisdictions adopting ISSB",
            "Organisations answering investor climate-risk questions"
        ],
        "prerequisites": [
            "Scope 1 and 2 inventory",
            "Climate risk and scenario analysis"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "csrd",
        "name": "CSRD / ESRS",
        "full_name": "Corporate Sustainability Reporting Directive (ESRS)",
        "stage": "report",
        "description": "Mandatory, assured EU reporting under the ESRS with double materiality.",
        "what_it_is": "EU legislation requiring in-scope companies to report against the European Sustainability Reporting Standards, with double materiality assessment, digital tagging and third-party assurance.",
        "who_needs_it": [
            "Large EU companies and EU-listed entities",
            "Non-EU groups with significant EU turnover and subsidiaries"
        ],
        "prerequisites": [
            "Double materiality assessment",
            "Value-chain data collection process",
            "Audit-ready internal controls over sustainability data"
        ],
        "region_applicability": ["eu", "global"]
    },
    {
        "slug": "brsr",
        "name": "BRSR",
        "full_name": "Business Responsibility & Sustainability Report (India)",
        "stage": "report",
        "description": "SEBI-mandated ESG disclosure format for large listed Indian companies.",
        "what_it_is": "A prescribed disclosure format structured around the nine NGRBC principles, with essential and leadership indicators, plus BRSR Core attributes subject to reasonable assurance.",
        "who_needs_it": [
            "Top-listed companies on Indian exchanges",
            "Value-chain partners of listed Indian companies"
        ],
        "prerequisites": [
            "Energy, water, waste and emissions data",
            "Workforce and social metrics"
        ],
        "region_applicability": ["india"]
    },
    {
        "slug": "tcfd",
        "name": "TCFD",
        "full_name": "Task Force on Climate-related Financial Disclosures",
        "stage": "report",
        "description": "Climate risk disclosure structure now carried forward inside IFRS S2.",
        "what_it_is": "A four-pillar framework — governance, strategy, risk management, metrics and targets — for disclosing climate-related financial risks and opportunities, including scenario analysis.",
        "who_needs_it": [
            "Companies answering lender or investor climate risk questionnaires",
            "Organisations transitioning toward ISSB reporting"
        ],
        "prerequisites": [
            "Board oversight of climate",
            "Climate scenario analysis"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "cdp",
        "name": "CDP",
        "full_name": "CDP Disclosure (Climate, Water, Forests)",
        "stage": "report",
        "description": "Questionnaire-based disclosure often requested by customers and investors.",
        "what_it_is": "An annual scored questionnaire covering climate change, water security and forests, widely used by procurement teams and investors to benchmark suppliers.",
        "who_needs_it": [
            "Suppliers to large corporates that cascade CDP requests",
            "Companies wanting an external benchmark score"
        ],
        "prerequisites": [
            "Scope 1, 2 and material Scope 3 data",
            "Targets and governance detail"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "sbti",
        "name": "SBTi",
        "full_name": "Science Based Targets initiative",
        "stage": "improve",
        "description": "Validated emissions targets aligned to 1.5°C pathways.",
        "what_it_is": "A target-setting and validation process. Companies submit near-term (and optionally net-zero) targets, which are checked against sector pathways and published once approved.",
        "who_needs_it": [
            "Companies committing publicly to net zero",
            "Suppliers whose customers require validated targets"
        ],
        "prerequisites": [
            "A complete base-year Scope 1, 2 and screened Scope 3 inventory",
            "Executive sign-off on a reduction trajectory"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "net-zero-standard",
        "name": "Net-Zero Standard",
        "full_name": "Corporate Net-Zero Standard",
        "stage": "improve",
        "description": "Rules for what a credible corporate net-zero claim requires.",
        "what_it_is": "Defines long-term deep decarbonisation (typically ~90%) before any neutralisation of residual emissions, plus interim near-term targets and beyond-value-chain mitigation guidance.",
        "who_needs_it": [
            "Organisations that have already published a net-zero ambition",
            "Companies needing to defend claims against greenwashing scrutiny"
        ],
        "prerequisites": [
            "Validated near-term science-based targets",
            "Scope 3 reduction plan"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "sdgs",
        "name": "UN SDGs",
        "full_name": "United Nations Sustainable Development Goals",
        "stage": "improve",
        "description": "A shared 17-goal language for framing sustainability strategy and impact.",
        "what_it_is": "Seventeen global goals with 169 targets. Companies map material activities to specific SDG targets and indicators rather than claiming whole goals.",
        "who_needs_it": [
            "Organisations communicating purpose to employees, customers and communities",
            "Companies working with development finance or public sector buyers"
        ],
        "prerequisites": [
            "Materiality view of where the business genuinely contributes"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    },
    {
        "slug": "renewable-energy-plan",
        "name": "Renewable Energy Roadmap",
        "full_name": "Renewable Energy Sourcing Roadmap (RE100-style)",
        "stage": "improve",
        "description": "A staged plan to shift purchased electricity to renewable sources.",
        "what_it_is": "A commitment and plan to source electricity from renewables through on-site generation, PPAs or attribute certificates, with milestones and a claims methodology.",
        "who_needs_it": [
            "Electricity-intensive operations with large Scope 2 footprints",
            "Companies with Scope 2 reduction targets"
        ],
        "prerequisites": [
            "Site-level electricity consumption data",
            "Market-based Scope 2 accounting"
        ],
        "region_applicability": ["global", "eu", "na", "uk", "india", "apac", "latam"]
    }
]

def seed_frameworks(db: Session) -> int:
    """
    Idempotently seeds the 16 frameworks into the database.
    Returns the number of frameworks inserted or updated.
    """
    count = 0
    for data in INITIAL_FRAMEWORKS:
        existing = db.query(Framework).filter_by(slug=data["slug"]).first()
        if not existing:
            framework = Framework(**data)
            db.add(framework)
            count += 1
        else:
            # Update fields in case metadata changed
            for k, v in data.items():
                setattr(existing, k, v)
    db.commit()
    return len(INITIAL_FRAMEWORKS)

if __name__ == "__main__":
    from app.db.database import SessionLocal, engine, Base
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_frameworks(db)
        print(f"Successfully seeded/verified {count} frameworks in the catalog.")
    finally:
        db.close()
