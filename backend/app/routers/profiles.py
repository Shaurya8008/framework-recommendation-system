from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import OrgProfile
from app.schemas import OrgProfileCreate, OrgProfileRead

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=OrgProfileRead, status_code=status.HTTP_201_CREATED)
def create_or_update_profile(profile_in: OrgProfileCreate, db: Session = Depends(get_db)):
    """
    Create or update an organization profile.
    """
    db_profile = OrgProfile(
        organization_name=profile_in.organization_name,
        industry=profile_in.industry,
        size=profile_in.size,
        region=profile_in.region,
        energy_use_level=profile_in.energy_use_level,
        emissions_maturity=profile_in.emissions_maturity,
        certifications=profile_in.certifications,
        disclosure_level=profile_in.disclosure_level,
        goals=profile_in.goals
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
