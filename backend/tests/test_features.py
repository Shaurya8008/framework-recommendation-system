import pytest
from src.features import compute_domain_scores, extract_features_dataframe


def test_compute_domain_scores_basic():
    profile = {
        "emissions_maturity": "none",
        "disclosure_level": "none",
        "certifications": [],
        "goals": []
    }
    scores = compute_domain_scores(profile)
    assert scores["emission_maturity_score"] == 0.0
    assert scores["reporting_score"] == 0.0
    assert scores["compliance_score"] == 0.0
    assert scores["target_readiness_score"] == 0.0


def test_compute_domain_scores_advanced():
    profile = {
        "emissions_maturity": "advanced",
        "disclosure_level": "full",
        "size": "5000+",
        "region": "eu",
        "certifications": ["iso-14001", "iso-50001", "iso-45001"],
        "goals": ["net-zero", "sbti", "sdg"]
    }
    scores = compute_domain_scores(profile)
    assert scores["emission_maturity_score"] == 1.0
    assert scores["reporting_score"] == 1.0  # min(1.0, 1.0 + 0.3)
    assert scores["compliance_score"] == 1.0  # 3 EMS certs / 3.0
    assert scores["target_readiness_score"] == 1.0  # (3/3)*0.6 + 1.0*0.4


def test_extract_features_dataframe():
    profiles = [
        {"industry": "manufacturing", "size": "1000-5000", "region": "eu", "certifications": ["iso-14001"]},
        {"industry": "technology", "size": "1-50", "region": "na", "certifications": []}
    ]
    df = extract_features_dataframe(profiles)
    assert len(df) == 2
    assert "emission_maturity_score" in df.columns
    assert "cert_iso_14001" in df.columns
    assert df.loc[0, "cert_iso_14001"] == 1
    assert df.loc[1, "cert_iso_14001"] == 0
    assert df.loc[0, "is_eu"] == 1
    assert df.loc[1, "is_eu"] == 0
