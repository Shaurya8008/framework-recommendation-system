from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Framework
from app.schemas import FrameworkRead

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


@router.get("", response_model=list[FrameworkRead])
def list_frameworks(
    stage: Optional[str] = Query(None, description="Filter by stage: manage | measure | report | improve"),
    topic: Optional[str] = Query(None, description="Filter by topic: climate | energy | water | waste | governance | social | reporting | supply_chain | finance | circularity"),
    geography: Optional[str] = Query(None, description="Filter by geography applicability: global | india | eu | us | uk"),
    mandatory_status: Optional[str] = Query(None, description="Filter by mandatory status: mandatory | quasi_mandatory | voluntary"),
    active_only: bool = Query(True, description="Only return active frameworks"),
    db: Session = Depends(get_db),
):
    """
    List the framework catalog with optional filtering.
    Supports filtering by stage, topic, geography, and mandatory_status.
    """
    query = db.query(Framework)

    if active_only:
        query = query.filter(Framework.active == True)

    if stage:
        query = query.filter(Framework.stage == stage.lower())

    if topic:
        query = query.filter(Framework.topic == topic.lower())

    if mandatory_status:
        query = query.filter(Framework.mandatory_status == mandatory_status.lower())

    if geography:
        # JSON array contains check — works with SQLite and PostgreSQL
        query = query.filter(Framework.geography_applicability.contains(geography.lower()))

    frameworks = query.order_by(Framework.stage, Framework.priority_weight.desc(), Framework.id).all()
    return frameworks


@router.get("/{slug_or_id}", response_model=FrameworkRead)
def get_framework(slug_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific framework by its slug or numeric ID.
    Includes full recommendation metadata for "why recommended" and
    "what is required to adopt it" views.
    """
    if slug_or_id.isdigit():
        framework = db.query(Framework).filter(Framework.id == int(slug_or_id)).first()
    else:
        framework = db.query(Framework).filter(Framework.slug == slug_or_id).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework
