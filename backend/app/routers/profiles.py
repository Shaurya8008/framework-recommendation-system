from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import OrgProfile
from app.schemas import OrgProfileCreate, OrgProfileRead

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=OrgProfileRead, status_code=status.HTTP_201_CREATED)
def create_or_update_profile(profile_in: OrgProfileCreate, db: Session = Depends(get_db)):
    """
    Create or update an organization profile with all sustainability fields.
    """
    db_profile = OrgProfile(
        organization_name=profile_in.organization_name,
        industry=profile_in.industry,
        subindustry=profile_in.subindustry,
        size=profile_in.size,
        org_size=profile_in.org_size,
        region=profile_in.region,
        is_listed=profile_in.is_listed,
        energy_use_level=profile_in.energy_use_level,
        annual_energy_use_level=profile_in.annual_energy_use_level or profile_in.energy_use_level,
        emissions_maturity=profile_in.emissions_maturity,
        emissions_tracking_maturity=profile_in.emissions_tracking_maturity or profile_in.emissions_maturity,
        certifications=profile_in.certifications,
        existing_certifications=profile_in.existing_certifications or profile_in.certifications,
        disclosure_level=profile_in.disclosure_level,
        disclosure_obligations=profile_in.disclosure_obligations,
        goals=profile_in.goals,
        sustainability_goals=profile_in.sustainability_goals or profile_in.goals,
        supply_chain_complexity=profile_in.supply_chain_complexity,
        export_exposure=profile_in.export_exposure,
        water_intensity=profile_in.water_intensity,
        waste_intensity=profile_in.waste_intensity,
        facility_footprint=profile_in.facility_footprint,
        investor_pressure=profile_in.investor_pressure,
        customer_pressure=profile_in.customer_pressure,
        assurance_readiness=profile_in.assurance_readiness,
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/{profile_id}", response_model=OrgProfileRead)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a saved organization profile by ID.
    """
    profile = db.query(OrgProfile).filter(OrgProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Organization profile not found")
    return profile
