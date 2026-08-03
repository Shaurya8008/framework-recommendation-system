"""
Profile normalization layer.

Maps raw OrgProfileCreate / RecommendRequest data into a standardized
NormalizedProfile with defaults, validation, and alias resolution.
This is a pure function — no DB or side-effects.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# Size mapping from legacy to standardized
SIZE_TO_ORG_SIZE = {
    "1-50": "startup",
    "50-250": "sme",
    "250-1000": "mid",
    "1000-5000": "enterprise",
    "5000+": "enterprise",
}


@dataclass
class NormalizedProfile:
    """Standardized internal representation of an organization profile."""
    organization_name: str = "Your organization"
    industry: str = "manufacturing"
    subindustry: str | None = None
    org_size: str = "mid"  # startup | sme | mid | enterprise
    region: str = "global"
    is_listed: bool = False
    annual_energy_use_level: str = "moderate"  # low | moderate | high | very-high
    emissions_tracking_maturity: str = "none"  # none | basic | intermediate | advanced
    existing_certifications: list[str] = field(default_factory=list)
    disclosure_obligations: list[str] = field(default_factory=list)
    sustainability_goals: list[str] = field(default_factory=list)
    supply_chain_complexity: str = "low"  # low | medium | high
    export_exposure: list[str] = field(default_factory=list)
    water_intensity: str = "low"  # low | medium | high
    waste_intensity: str = "low"  # low | medium | high
    facility_footprint: str = "single_site"  # single_site | multi_site
    investor_pressure: str = "low"  # low | medium | high
    customer_pressure: str = "low"  # low | medium | high
    assurance_readiness: str = "low"  # low | medium | high


def _get(obj: Any, attr: str, default: Any = "") -> Any:
    """Get attribute from dict or object."""
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def normalize_profile(raw: Any) -> NormalizedProfile:
    """
    Normalize a raw profile (dict, ORM object, or Pydantic model) into
    a NormalizedProfile dataclass with consistent field names and defaults.
    """
    # --- Organization name ---
    org_name = (
        _get(raw, "organization_name")
        or _get(raw, "organizationName")
        or "Your organization"
    )

    # --- Industry ---
    industry = _get(raw, "industry", "manufacturing") or "manufacturing"
    subindustry = _get(raw, "subindustry", None)

    # --- Size normalization ---
    org_size = _get(raw, "org_size", None)
    if not org_size:
        legacy_size = _get(raw, "size", "250-1000") or "250-1000"
        org_size = SIZE_TO_ORG_SIZE.get(legacy_size, "mid")

    # --- Region ---
    region = (_get(raw, "region", "global") or "global").lower()

    # --- Listed status ---
    is_listed = bool(_get(raw, "is_listed", False))

    # --- Energy level ---
    energy = (
        _get(raw, "annual_energy_use_level")
        or _get(raw, "energy_use_level")
        or _get(raw, "energyUse")
        or "moderate"
    )

    # --- Emissions maturity ---
    emissions = (
        _get(raw, "emissions_tracking_maturity")
        or _get(raw, "emissions_maturity")
        or "none"
    )

    # --- Certifications ---
    certs = _get(raw, "existing_certifications", None) or _get(raw, "certifications", None) or []
    if isinstance(certs, str):
        certs = [certs]

    # --- Disclosure ---
    disclosure_obligations = _get(raw, "disclosure_obligations", None) or []
    disclosure_level = _get(raw, "disclosure_level", None) or _get(raw, "disclosure", None) or "none"
    if disclosure_level not in ("none", None) and not disclosure_obligations:
        disclosure_obligations = [disclosure_level]

    # --- Goals ---
    goals = _get(raw, "sustainability_goals", None) or _get(raw, "goals", None) or []
    if isinstance(goals, str):
        goals = [goals]

    # --- Supply chain ---
    sc = _get(raw, "supply_chain_complexity", "low") or "low"

    # --- Export exposure ---
    export = _get(raw, "export_exposure", None) or []
    if isinstance(export, str):
        export = [export]

    # --- Intensities ---
    water = _get(raw, "water_intensity", "low") or "low"
    waste = _get(raw, "waste_intensity", "low") or "low"

    # --- Facility ---
    facility = _get(raw, "facility_footprint", "single_site") or "single_site"

    # --- Pressures ---
    investor = _get(raw, "investor_pressure", "low") or "low"
    customer = _get(raw, "customer_pressure", "low") or "low"

    # --- Assurance readiness ---
    assurance = _get(raw, "assurance_readiness", "low") or "low"

    return NormalizedProfile(
        organization_name=org_name,
        industry=industry,
        subindustry=subindustry,
        org_size=org_size,
        region=region,
        is_listed=is_listed,
        annual_energy_use_level=energy,
        emissions_tracking_maturity=emissions,
        existing_certifications=certs,
        disclosure_obligations=disclosure_obligations,
        sustainability_goals=goals,
        supply_chain_complexity=sc,
        export_exposure=export,
        water_intensity=water,
        waste_intensity=waste,
        facility_footprint=facility,
        investor_pressure=investor,
        customer_pressure=customer,
        assurance_readiness=assurance,
    )
