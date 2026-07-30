from app.db.models import Framework, OrgProfile, Recommendation
from app.db.seed import seed_frameworks


def test_seed_frameworks(db_session):
    # Ensure frameworks are seeded in the fixture
    frameworks = db_session.query(Framework).all()
    assert len(frameworks) == 16
    slugs = {f.slug for f in frameworks}
    assert "iso-14001" in slugs
    assert "ghg-protocol" in slugs
    assert "csrd" in slugs

    # Calling seed again should be idempotent
    count = seed_frameworks(db_session)
    assert count == 16
    assert db_session.query(Framework).count() == 16


def test_create_org_profile_and_recommendation(db_session):
    profile = OrgProfile(
        organization_name="Test Org",
        industry="energy",
        size="5000+",
        region="eu",
        energy_use_level="very-high",
        emissions_maturity="advanced",
        certifications=["iso-14001"],
        disclosure_level="full",
        goals=["net-zero"]
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    assert profile.id is not None

    rec = Recommendation(
        org_profile_id=profile.id,
        framework_id=1,
        framework_slug="iso-14001",
        score=88.0,
        reason="Test reason",
        stage="manage"
    )
    db_session.add(rec)
    db_session.commit()
    db_session.refresh(rec)
    assert rec.id is not None
    assert rec.org_profile.organization_name == "Test Org"
