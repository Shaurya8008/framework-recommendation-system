"""
Explainability module.

Generates human-readable explanations for each recommendation:
- why_recommended: primary reason
- why_now: urgency / timing signal
- recommendation_type: foundational | compliance | disclosure | target | advanced
- confidence_label: high | medium | low
"""

from __future__ import annotations
from typing import Any

from src.normalize_profile import NormalizedProfile


STAGE_TO_DEFAULT_TYPE: dict[str, str] = {
    "manage": "foundational",
    "measure": "foundational",
    "report": "disclosure",
    "improve": "target",
}


def _classify_recommendation_type(
    slug: str,
    stage: str,
    mandatory_status: str,
    score: float,
) -> str:
    """Determine the recommendation type category."""
    if mandatory_status in ("mandatory", "quasi_mandatory"):
        return "compliance"
    if stage == "manage":
        return "foundational"
    if stage == "measure":
        return "foundational"
    if stage == "report":
        return "disclosure"
    if stage == "improve":
        if score >= 70:
            return "target"
        return "advanced"
    return STAGE_TO_DEFAULT_TYPE.get(stage, "foundational")


def _compute_confidence(
    score: float,
    boost_reasons: list[str],
    missing_prerequisites: list[str],
) -> str:
    """Determine confidence label based on score and evidence."""
    if score >= 75 and len(boost_reasons) >= 2 and not missing_prerequisites:
        return "high"
    if score >= 50 and len(boost_reasons) >= 1:
        return "medium"
    return "low"


def _generate_why_recommended(
    profile: NormalizedProfile,
    scored_item: dict[str, Any],
) -> str:
    """Generate the primary recommendation reason."""
    boost_reasons = scored_item.get("boost_reasons", [])
    template = scored_item.get("why_recommended_template", "")
    slug = scored_item.get("slug", "")
    name = scored_item.get("name", slug)
    stage = scored_item.get("stage", "")

    # If we have specific boost reasons, compose from them
    if boost_reasons:
        # Use the top 2 most relevant reasons
        top_reasons = boost_reasons[:2]
        reason_text = "; ".join(top_reasons)
        return f"Recommended for {profile.organization_name}: {reason_text}."

    # Fall back to template
    if template:
        try:
            return template.format(
                reason="your profile indicates this framework is relevant",
                industry=profile.industry,
                energy_level=profile.annual_energy_use_level,
                complexity=profile.supply_chain_complexity,
            )
        except (KeyError, IndexError):
            pass

    # Generic fallback
    return f"{name} is recommended for the {stage.upper()} stage of your sustainability journey based on your organization profile."


def _generate_why_now(
    profile: NormalizedProfile,
    scored_item: dict[str, Any],
) -> str:
    """Generate timing/urgency explanation."""
    slug = scored_item.get("slug", "")
    mandatory = scored_item.get("mandatory_status", "voluntary")
    missing = scored_item.get("missing_prerequisites", [])
    stage = scored_item.get("stage", "")

    # Mandatory = urgent
    if mandatory == "mandatory":
        if profile.region == "india" and slug in ("brsr", "brsr-core"):
            return "This disclosure is SEBI-mandated for listed Indian companies — compliance timelines are already in effect."
        if profile.region == "eu" and slug in ("csrd", "esrs"):
            return "CSRD reporting requirements are phasing in — early preparation reduces compliance risk."
        return "This is a mandatory requirement — timely adoption avoids regulatory risk."

    if mandatory == "quasi_mandatory":
        return "While not strictly mandatory today, adoption of this standard is becoming a market expectation and may become required."

    # No emissions tracking → measurement is urgent
    if profile.emissions_tracking_maturity == "none" and stage == "measure":
        return "Starting emissions measurement now establishes the baseline that all reporting and target frameworks require."

    # Missing prerequisites → sequential urgency
    if missing:
        prereq_names = ", ".join(missing)
        return f"Consider addressing prerequisites ({prereq_names}) first, then adopt this framework as a natural next step."

    # Foundation stage
    if stage == "manage":
        return "Management systems provide the governance foundation — establishing them early prevents rework when reporting requirements arrive."

    if stage == "improve":
        return "Target-setting frameworks are most impactful once measurement and reporting foundations are in place."

    return "Now is a good time to begin — your profile indicates readiness for this framework."


def generate_explanations(
    profile: NormalizedProfile,
    scored_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Enrich each scored item with explainability fields:
    - why_recommended
    - why_now
    - recommendation_type
    - confidence_label
    - reason (legacy field — same as why_recommended)
    """
    enriched: list[dict[str, Any]] = []

    for item in scored_items:
        why_recommended = _generate_why_recommended(profile, item)
        why_now = _generate_why_now(profile, item)
        rec_type = _classify_recommendation_type(
            item.get("slug", ""),
            item.get("stage", ""),
            item.get("mandatory_status", "voluntary"),
            item.get("score", 0),
        )
        confidence = _compute_confidence(
            item.get("score", 0),
            item.get("boost_reasons", []),
            item.get("missing_prerequisites", []),
        )

        enriched_item = {
            **item,
            "why_recommended": why_recommended,
            "why_now": why_now,
            "reason": why_recommended,  # legacy compatibility
            "recommendation_type": rec_type,
            "confidence_label": confidence,
        }
        enriched.append(enriched_item)

    return enriched
