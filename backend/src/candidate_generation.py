"""
Candidate generation module.

Implements broad, high-recall filtering of the framework catalog
into candidates relevant to a normalized organization profile.
"""

from __future__ import annotations
from typing import Any

from src.normalize_profile import NormalizedProfile


def _get(obj: Any, attr: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


# Stage-level trigger logic helpers

def _should_trigger_manage(profile: NormalizedProfile) -> bool:
    """MANAGE frameworks recommended when governance/operational foundations are weak."""
    certs = set(profile.existing_certifications)
    has_ems = bool(certs & {"iso-14001", "iso-50001", "iso-45001"})
    return (
        not has_ems
        or profile.emissions_tracking_maturity in ("none", "basic")
        or profile.facility_footprint == "multi_site"
    )


def _should_trigger_measure(profile: NormalizedProfile) -> bool:
    """MEASURE frameworks recommended when quantification gaps exist."""
    return (
        profile.emissions_tracking_maturity in ("none", "basic", "intermediate")
        or profile.investor_pressure in ("medium", "high")
        or profile.customer_pressure in ("medium", "high")
        or any(g in profile.sustainability_goals for g in
               ["net_zero", "decarbonization", "reporting_improvement", "measurement"])
    )


def _should_trigger_report(profile: NormalizedProfile) -> bool:
    """REPORT frameworks recommended when disclosure pressure exists."""
    return (
        profile.is_listed
        or profile.region in ("eu", "india")
        or "eu" in profile.export_exposure
        or profile.investor_pressure in ("medium", "high")
        or any(g in profile.sustainability_goals for g in
               ["reporting_improvement", "disclosure", "transparency"])
        or profile.emissions_tracking_maturity in ("basic", "intermediate", "advanced")
    )


def _should_trigger_improve(profile: NormalizedProfile) -> bool:
    """IMPROVE frameworks recommended when organisation is ready for ambition/targets."""
    return (
        profile.emissions_tracking_maturity in ("basic", "intermediate", "advanced")
        or any(g in profile.sustainability_goals for g in
               ["net_zero", "decarbonization", "renewable_energy", "energy_productivity",
                "electrification", "fleet_transition", "circularity", "zero_waste",
                "sdg", "sbti"])
    )


STAGE_TRIGGERS = {
    "manage": _should_trigger_manage,
    "measure": _should_trigger_measure,
    "report": _should_trigger_report,
    "improve": _should_trigger_improve,
}


def _geography_match(framework: Any, profile: NormalizedProfile) -> bool:
    """
    Lenient geography match.
    Returns True if the framework applies to the profile's region,
    if the framework is global, or if the profile has export_exposure
    matching the framework geography.
    """
    geo = _get(framework, "geography_applicability", ["global"]) or ["global"]

    # Global frameworks apply to everyone
    if "global" in geo:
        return True

    # Direct region match
    if profile.region in geo:
        return True

    # Export exposure match (e.g., Indian company with EU export exposure → CSRD applies)
    if profile.export_exposure:
        if set(profile.export_exposure) & set(geo):
            return True

    return False


def _industry_match(framework: Any, profile: NormalizedProfile) -> bool:
    """
    Lenient industry match.
    Returns True if the framework fits the profile's industry
    or if the framework has no industry restrictions.
    """
    industry_fit = _get(framework, "industry_fit", []) or []
    if not industry_fit:
        return True  # No restriction = applies to all
    return profile.industry in industry_fit


def _org_size_match(framework: Any, profile: NormalizedProfile) -> bool:
    """
    Lenient org size match.
    Returns True if the framework fits the profile's org_size
    or if the framework has no size restrictions.
    """
    size_fit = _get(framework, "org_size_fit", []) or []
    if not size_fit:
        return True
    return profile.org_size in size_fit


def generate_candidates(
    profile: NormalizedProfile,
    catalog: list[Any],
) -> list[dict[str, Any]]:
    """
    Generate a broad candidate list from the framework catalog.

    Strategy:
    1. Start from all active frameworks
    2. Filter by geography (lenient)
    3. Filter by industry (lenient)
    4. Filter by org size (lenient)
    5. Always include mandatory frameworks
    6. Always include dependency-adjacent frameworks
    7. Check stage trigger conditions

    Returns list of framework dicts/objects that passed filtering.
    """
    # Determine which stages are triggered
    triggered_stages: set[str] = set()
    for stage, trigger_fn in STAGE_TRIGGERS.items():
        if trigger_fn(profile):
            triggered_stages.add(stage)

    # Always include at least manage and measure as baseline
    triggered_stages.add("manage")
    triggered_stages.add("measure")

    candidates: list[Any] = []
    included_slugs: set[str] = set()

    for fw in catalog:
        # Skip inactive frameworks
        if not _get(fw, "active", True):
            continue

        slug = _get(fw, "slug", "")
        stage = _get(fw, "stage", "manage")
        mandatory = _get(fw, "mandatory_status", "voluntary")

        # Always include mandatory/quasi-mandatory frameworks (if geography matches at all)
        if mandatory in ("mandatory", "quasi_mandatory"):
            if _geography_match(fw, profile):
                candidates.append(fw)
                included_slugs.add(slug)
                continue

        # Stage must be triggered
        if stage not in triggered_stages:
            continue

        # Apply lenient filters — must pass at least geography OR be dependency-adjacent
        geo_ok = _geography_match(fw, profile)
        ind_ok = _industry_match(fw, profile)
        size_ok = _org_size_match(fw, profile)

        if geo_ok and (ind_ok or size_ok):
            candidates.append(fw)
            included_slugs.add(slug)

    # Second pass: include dependency-adjacent frameworks not yet included
    for fw in catalog:
        if not _get(fw, "active", True):
            continue
        slug = _get(fw, "slug", "")
        if slug in included_slugs:
            continue

        depends_on = _get(fw, "depends_on", []) or []
        recommended_next = _get(fw, "recommended_next", []) or []

        # If a candidate depends on a framework we already included, include it
        if set(depends_on) & included_slugs:
            candidates.append(fw)
            included_slugs.add(slug)
            continue

        # If an included framework recommends this one as next, include it
        for candidate in candidates:
            c_next = _get(candidate, "recommended_next", []) or []
            if slug in c_next:
                candidates.append(fw)
                included_slugs.add(slug)
                break

    return candidates
