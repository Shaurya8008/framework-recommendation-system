from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Framework
from app.schemas import FrameworkRead

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


@router.get("", response_model=list[FrameworkRead])
def list_frameworks(db: Session = Depends(get_db)):
    """
    List the framework catalog (for admin and detail views).
    """
    frameworks = db.query(Framework).order_by(Framework.id).all()
    return frameworks


@router.get("/{slug_or_id}", response_model=FrameworkRead)
def get_framework(slug_or_id: str, db: Session = Depends(get_db)):
    """
    Retrieve details for a specific framework by its slug or numeric ID.
    """
    if slug_or_id.isdigit():
        framework = db.query(Framework).filter(Framework.id == int(slug_or_id)).first()
    else:
        framework = db.query(Framework).filter(Framework.slug == slug_or_id).first()

    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework
