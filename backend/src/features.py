from typing import Any
import pandas as pd
import numpy as np

INDUSTRIES = ["manufacturing", "energy", "chemicals", "construction", "transport", "technology", "consumer-goods", "agriculture", "financial", "healthcare"]
SIZES = ["1-50", "50-250", "250-1000", "1000-5000", "5000+"]
REGIONS = ["global", "eu", "na", "uk", "india", "apac", "latam"]
ENERGY_LEVELS = ["low", "moderate", "high", "very-high"]
MATURITIES = ["none", "basic", "advanced"]
DISCLOSURES = ["none", "partial", "full"]

CERT_SLUGS = ["iso-14001", "iso-50001", "iso-45001", "iso-14064"]
GOAL_SLUGS = ["net-zero", "sbti", "sdg", "renewables", "stakeholder-trust"]


def _get_val(profile: Any, attr: str, default: Any = "") -> Any:
    if isinstance(profile, dict):
        return profile.get(attr, default)
    return getattr(profile, attr, default)


def compute_domain_scores(profile: Any) -> dict[str, float]:
    """
    Computes domain-specific sustainability feature scores for an organization profile:
    - emission_maturity_score
    - reporting_score
    - compliance_score
    - target_readiness_score
    """
    emissions_mat = _get_val(profile, "emissions_maturity", "none")
    disclosure = _get_val(profile, "disclosure_level", "none") or _get_val(profile, "disclosure", "none")
    certifications = _get_val(profile, "certifications", []) or []
    goals = _get_val(profile, "goals", []) or []
    size = _get_val(profile, "size", "")
    region = _get_val(profile, "region", "")

    # 1. emission_maturity_score
    mat_map = {"none": 0.0, "basic": 0.5, "advanced": 1.0}
    ems_score = mat_map.get(emissions_mat, 0.0)

    # 2. reporting_score
    disc_map = {"none": 0.0, "partial": 0.5, "full": 1.0}
    rep_score = disc_map.get(disclosure, 0.0)
    if size in ["1000-5000", "5000+"] or region in ["eu", "india"]:
        rep_score = min(1.0, rep_score + 0.3)

    # 3. compliance_score
    ems_certs = [c for c in certifications if c in ["iso-14001", "iso-50001", "iso-45001"]]
    comp_score = min(1.0, len(ems_certs) / 3.0)

    # 4. target_readiness_score
    target_goals = [g for g in goals if g in ["net-zero", "sbti", "sdg", "renewables"]]
    tr_score = min(1.0, (len(target_goals) / 3.0) * 0.6 + ems_score * 0.4)

    return {
        "emission_maturity_score": round(ems_score, 4),
        "reporting_score": round(rep_score, 4),
        "compliance_score": round(comp_score, 4),
        "target_readiness_score": round(tr_score, 4),
    }


def extract_features_dataframe(profiles: list[Any]) -> pd.DataFrame:
    """
    Converts a list of profile dicts/objects into a numeric feature DataFrame suitable
    for scikit-learn / XGBoost classifiers and rankers.
    """
    rows = []
    for p in profiles:
        domain_scores = compute_domain_scores(p)
        certifications = set(_get_val(p, "certifications", []) or [])
        goals = set(_get_val(p, "goals", []) or [])
        ind = _get_val(p, "industry", "manufacturing")
        size = _get_val(p, "size", "250-1000")
        reg = _get_val(p, "region", "global")
        energy = _get_val(p, "energy_use_level", "moderate") or _get_val(p, "energyUse", "moderate")
        mat = _get_val(p, "emissions_maturity", "none")
        disc = _get_val(p, "disclosure_level", "none") or _get_val(p, "disclosure", "none")

        row = {
            **domain_scores,
            "size_num": {"1-50": 1, "50-250": 2, "250-1000": 3, "1000-5000": 4, "5000+": 5}.get(size, 3),
            "energy_num": {"low": 1, "moderate": 2, "high": 3, "very-high": 4}.get(energy, 2),
            "is_heavy_industry": int(ind in ["manufacturing", "energy", "chemicals", "construction", "transport"]),
            "is_eu": int(reg == "eu"),
            "is_india": int(reg == "india"),
            "is_large": int(size in ["1000-5000", "5000+"]),
        }

        # One-hot flags for certifications
        for c in CERT_SLUGS:
            row[f"cert_{c.replace('-', '_')}"] = int(c in certifications)

        # One-hot flags for goals
        for g in GOAL_SLUGS:
            row[f"goal_{g.replace('-', '_')}"] = int(g in goals)

        rows.append(row)

    df = pd.DataFrame(rows)
    return df
