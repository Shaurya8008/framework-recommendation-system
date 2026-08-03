"""
Transparent rule-based scoring engine.

Produces a numeric score for each candidate framework based on:
- geography fit
- industry fit
- obligation/mandatory fit
- maturity fit
- goal alignment
- dependency fit
- framework priority weight
- complexity penalty
- missing prerequisite penalty
- duplication penalty

All weights are configurable in SCORING_WEIGHTS.
Designed so ML scoring can replace or augment this later.
"""

from __future__ import annotations
from typing import Any

from src.normalize_profile import NormalizedProfile


# ---------------------------------------------------------------------------
# Configurable scoring weights — single source of truth
# ---------------------------------------------------------------------------

SCORING_WEIGHTS: dict[str, float] = {
    "mandatory_obligation": 30.0,
    "quasi_mandatory_obligation": 20.0,
    "strong_geography_fit": 15.0,
    "moderate_geography_fit": 8.0,
    "strong_industry_fit": 15.0,
    "moderate_industry_fit": 7.0,
    "goal_alignment": 10.0,
    "strong_goal_alignment": 18.0,
    "maturity_match": 10.0,
    "prerequisite_satisfied": 10.0,
    "missing_prerequisite_penalty": -20.0,
    "too_advanced_penalty": -15.0,
    "overlapping_duplicate_penalty": -5.0,
    "base_score": 20.0,
}


def _get(obj: Any, attr: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


# ---------------------------------------------------------------------------
# Maturity ordering for comparison
# ---------------------------------------------------------------------------

MATURITY_ORDER = {"none": 0, "basic": 1, "intermediate": 2, "advanced": 3}


def _maturity_level(val: str) -> int:
    return MATURITY_ORDER.get(val, 0)


# ---------------------------------------------------------------------------
# Profile-to-framework boost rules
# ---------------------------------------------------------------------------

def _compute_profile_boosts(profile: NormalizedProfile, fw: Any) -> tuple[float, list[str]]:
    """
    Apply the detailed profile-to-framework scoring/boost rules.
    Returns (boost_score, list_of_reasons).
    """
    slug = _get(fw, "slug", "")
    boost = 0.0
    reasons: list[str] = []

    # --- India + listed → BRSR ---
    if profile.region == "india" and profile.is_listed:
        if slug == "brsr":
            boost += 25.0
            reasons.append("strongly boosted because you are a listed company in India")
        elif slug == "brsr-core" and profile.assurance_readiness in ("medium", "high"):
            boost += 18.0
            reasons.append("boosted because your assurance readiness supports BRSR Core requirements")

    # --- EU or EU export exposure → CSRD/ESRS ---
    if profile.region == "eu" or "eu" in profile.export_exposure:
        if slug == "csrd":
            boost += 25.0
            reasons.append("strongly boosted because your EU presence triggers CSRD applicability")
        elif slug == "esrs":
            boost += 22.0
            reasons.append("strongly boosted as ESRS provides the detailed standards under CSRD")

    # --- Investor pressure → IFRS/SASB/TCFD ---
    if profile.investor_pressure in ("medium", "high"):
        if slug == "ifrs-s1":
            boost += 15.0
            reasons.append("boosted because investor pressure makes IFRS S1 disclosure relevant")
        elif slug == "ifrs-s2":
            boost += 15.0
            reasons.append("boosted because investor pressure makes climate disclosure relevant")
        elif slug == "sasb":
            boost += 10.0
            reasons.append("boosted because investors reference SASB for industry-specific metrics")
        elif slug == "tcfd":
            boost += 12.0
            reasons.append("boosted because investors expect TCFD-aligned climate risk disclosure")

    # --- Emissions tracking maturity ---
    if profile.emissions_tracking_maturity == "none":
        if slug == "ghg-protocol-corporate":
            boost += 25.0
            reasons.append("strongly boosted because you have no emissions tracking — GHG Protocol is the starting point")
    elif profile.emissions_tracking_maturity in ("basic", "intermediate"):
        if slug == "iso-14064-1":
            boost += 12.0
            reasons.append("boosted because your existing inventory can benefit from verification readiness")

    # --- High energy use ---
    if profile.annual_energy_use_level in ("high", "very-high"):
        if slug == "iso-50001":
            boost += 18.0
            reasons.append("boosted because your high energy use makes energy management a priority")
        elif slug == "re100":
            boost += 12.0
            reasons.append("boosted because high electricity consumption makes renewable sourcing impactful")
        elif slug == "ep100":
            boost += 8.0
            reasons.append("boosted because high energy use supports an energy productivity commitment")

    # --- Missing environmental management ---
    if "iso-14001" not in profile.existing_certifications:
        if slug == "iso-14001":
            boost += 15.0
            reasons.append("boosted because you lack a formal environmental management system")

    # --- High water intensity ---
    if profile.water_intensity == "high":
        if slug == "iso-46001":
            boost += 12.0
            reasons.append("boosted because your high water intensity needs systematic management")
        elif slug == "iso-14046":
            boost += 10.0
            reasons.append("boosted because quantified water footprint assessment is relevant")
        elif slug == "aws-standard":
            boost += 10.0
            reasons.append("boosted because site-level water stewardship addresses your water risk")
        elif slug == "cdp-water":
            boost += 10.0
            reasons.append("boosted because water security disclosure is expected for water-intensive operations")

    # --- High supply chain complexity ---
    if profile.supply_chain_complexity in ("medium", "high"):
        if slug == "ghg-protocol-scope3":
            boost += 15.0
            reasons.append("boosted because your complex supply chain makes Scope 3 accounting material")
        elif slug == "iso-20400":
            boost += 10.0
            reasons.append("boosted because sustainable procurement governance helps manage supply chain risks")
        elif slug == "sa8000":
            boost += 10.0
            reasons.append("boosted because supply chain social accountability is expected")
        elif slug == "ecovadis":
            boost += 10.0
            reasons.append("boosted because supply chain sustainability rating is valuable")

    # --- Finance industry ---
    if profile.industry == "finance":
        if slug == "pcaf":
            boost += 18.0
            reasons.append("strongly boosted because financed emissions are likely your largest carbon impact")
        elif slug == "ifrs-s1":
            boost += 10.0
            reasons.append("boosted because financial sector faces strong investor disclosure expectations")
        elif slug == "ifrs-s2":
            boost += 10.0
            reasons.append("boosted because climate financial disclosure is critical for financial institutions")
        elif slug == "tcfd":
            boost += 10.0
            reasons.append("boosted because financial sector climate risk disclosure is widely expected")

    # --- Sustainability goals ---
    goals = set(profile.sustainability_goals)

    if goals & {"net_zero", "decarbonization"}:
        if slug == "sbti":
            boost += 22.0
            reasons.append("strongly boosted because your net-zero ambition needs SBTi validation")
        elif slug == "net-zero-standard":
            boost += 15.0
            reasons.append("boosted because net-zero claims need standardised evidence")

    if "renewable_energy" in goals:
        if slug == "re100":
            boost += 15.0
            reasons.append("boosted because you flagged renewable energy as a goal")

    if "energy_productivity" in goals:
        if slug == "ep100":
            boost += 12.0
            reasons.append("boosted because energy productivity improvement is a stated goal")

    if goals & {"electrification", "fleet_transition"}:
        if slug == "ev100":
            boost += 12.0
            reasons.append("boosted because fleet electrification aligns with your transition goals")

    if "reporting_improvement" in goals:
        if slug == "gri":
            boost += 12.0
            reasons.append("boosted because GRI provides the reporting structure you're seeking")
        # Geography-relevant disclosures
        if profile.region == "india" and slug == "brsr":
            boost += 8.0
            reasons.append("boosted because reporting improvement in India starts with BRSR alignment")
        if (profile.region == "eu" or "eu" in profile.export_exposure) and slug in ("csrd", "esrs"):
            boost += 8.0
            reasons.append("boosted because EU reporting improvement requires CSRD/ESRS readiness")
        if slug in ("ifrs-s1", "ifrs-s2"):
            boost += 6.0
            reasons.append("boosted because investor-facing reporting improvement includes ISSB standards")

    # --- Facility footprint ---
    if profile.facility_footprint == "multi_site":
        if slug == "iso-14001":
            boost += 8.0
            reasons.append("boosted because multi-site operations need systematic environmental governance")
        elif slug == "iso-50001":
            boost += 8.0
            reasons.append("boosted because multi-site energy management multiplies efficiency gains")

    # --- Customer pressure ---
    if profile.customer_pressure in ("medium", "high"):
        if slug == "cdp-climate":
            boost += 12.0
            reasons.append("boosted because customers commonly request CDP climate disclosure")
        elif slug == "cdp-water":
            boost += 8.0
            reasons.append("boosted because customers may request water security disclosure")
        elif slug == "ecovadis":
            boost += 12.0
            reasons.append("boosted because customers use EcoVadis ratings for supplier assessment")
        elif slug == "ghg-protocol-scope3":
            boost += 8.0
            reasons.append("boosted because customer-driven supply chain disclosure requires Scope 3 data")

    # --- Waste intensity ---
    if profile.waste_intensity == "high":
        if slug == "true-zero-waste":
            boost += 12.0
            reasons.append("boosted because your high waste generation supports a zero-waste certification pathway")
        elif slug == "circulytics":
            boost += 10.0
            reasons.append("boosted because circular economy measurement is relevant for your waste profile")

    return boost, reasons


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_framework(
    profile: NormalizedProfile,
    fw: Any,
    already_recommended_slugs: set[str] | None = None,
) -> dict[str, Any]:
    """
    Score a single framework against a normalized profile.

    Returns a dict with:
    - slug, name, stage, score, score_breakdown, boost_reasons
    """
    W = SCORING_WEIGHTS
    slug = _get(fw, "slug", "")
    name = _get(fw, "name", slug)
    stage = _get(fw, "stage", "manage")
    description = _get(fw, "description", "")
    fw_id = _get(fw, "id", None)
    mandatory = _get(fw, "mandatory_status", "voluntary")
    priority_weight = float(_get(fw, "priority_weight", 1.0) or 1.0)

    score = W["base_score"]
    breakdown: dict[str, float] = {"base": W["base_score"]}

    # 1. Obligation fit
    if mandatory == "mandatory":
        score += W["mandatory_obligation"]
        breakdown["obligation"] = W["mandatory_obligation"]
    elif mandatory == "quasi_mandatory":
        score += W["quasi_mandatory_obligation"]
        breakdown["obligation"] = W["quasi_mandatory_obligation"]

    # 2. Geography fit
    geo = _get(fw, "geography_applicability", ["global"]) or ["global"]
    if profile.region in geo and "global" not in geo:
        # Direct match to a region-specific framework
        score += W["strong_geography_fit"]
        breakdown["geography"] = W["strong_geography_fit"]
    elif "global" in geo:
        score += W["moderate_geography_fit"]
        breakdown["geography"] = W["moderate_geography_fit"]
    elif set(profile.export_exposure) & set(geo):
        score += W["moderate_geography_fit"]
        breakdown["geography"] = W["moderate_geography_fit"]

    # 3. Industry fit
    industry_fit = _get(fw, "industry_fit", []) or []
    if profile.industry in industry_fit:
        score += W["strong_industry_fit"]
        breakdown["industry"] = W["strong_industry_fit"]
    elif not industry_fit:
        score += W["moderate_industry_fit"]
        breakdown["industry"] = W["moderate_industry_fit"]

    # 4. Maturity fit
    mat_min = _get(fw, "maturity_min", "none") or "none"
    mat_max = _get(fw, "maturity_max", None)
    profile_mat = _maturity_level(profile.emissions_tracking_maturity)
    fw_min = _maturity_level(mat_min)
    fw_max = _maturity_level(mat_max) if mat_max else 3

    if fw_min <= profile_mat <= fw_max:
        score += W["maturity_match"]
        breakdown["maturity"] = W["maturity_match"]
    elif profile_mat < fw_min:
        # Too advanced for current maturity
        score += W["too_advanced_penalty"]
        breakdown["maturity"] = W["too_advanced_penalty"]

    # 5. Dependency / prerequisite fit
    depends_on = _get(fw, "depends_on", []) or []
    certs = set(profile.existing_certifications)
    missing_prereqs: list[str] = []

    if depends_on:
        satisfied = 0
        for dep in depends_on:
            if dep in certs:
                satisfied += 1
            else:
                missing_prereqs.append(dep)
        if satisfied == len(depends_on):
            score += W["prerequisite_satisfied"]
            breakdown["dependency"] = W["prerequisite_satisfied"]
        elif missing_prereqs:
            score += W["missing_prerequisite_penalty"] * (len(missing_prereqs) / len(depends_on))
            breakdown["dependency"] = W["missing_prerequisite_penalty"] * (len(missing_prereqs) / len(depends_on))

    # 6. Profile-specific boosts
    boost, boost_reasons = _compute_profile_boosts(profile, fw)
    score += boost
    breakdown["profile_boost"] = boost

    # 7. Framework priority weight
    weight_bonus = (priority_weight - 1.0) * 10.0  # e.g., 1.3 → +3 points
    score += weight_bonus
    breakdown["priority_weight"] = weight_bonus

    # 8. Duplication penalty
    if already_recommended_slugs:
        # Check for overlapping frameworks (e.g., BRSR and BRSR Core)
        topic = _get(fw, "topic", "")
        subtopic = _get(fw, "subtopic", "")
        overlap_count = 0
        for existing_slug in already_recommended_slugs:
            if existing_slug.startswith(slug.split("-")[0]) and existing_slug != slug:
                overlap_count += 1
        if overlap_count > 0:
            penalty = W["overlapping_duplicate_penalty"] * overlap_count
            score += penalty
            breakdown["duplication"] = penalty

    # Clamp score to [0, 100]
    score = max(0.0, min(100.0, score))

    return {
        "id": fw_id,
        "framework_id": fw_id,
        "slug": slug,
        "name": name,
        "stage": stage,
        "description": description,
        "score": round(score, 1),
        "score_breakdown": breakdown,
        "boost_reasons": boost_reasons,
        "missing_prerequisites": missing_prereqs,
        "depends_on": depends_on,
        "recommended_next": _get(fw, "recommended_next", []) or [],
        "prerequisites": _get(fw, "prerequisites", []) or [],
        "priority_weight": priority_weight,
        "mandatory_status": mandatory,
        "implementation_effort": _get(fw, "implementation_effort", "medium"),
        "why_recommended_template": _get(fw, "why_recommended_template", ""),
    }


def score_all_candidates(
    profile: NormalizedProfile,
    candidates: list[Any],
) -> list[dict[str, Any]]:
    """
    Score all candidate frameworks and return sorted results.
    """
    scored: list[dict[str, Any]] = []
    seen_slugs: set[str] = set()

    for fw in candidates:
        result = score_framework(profile, fw, already_recommended_slugs=seen_slugs)
        scored.append(result)
        seen_slugs.add(result["slug"])

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
