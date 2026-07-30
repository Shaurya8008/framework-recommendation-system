from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import OrgProfile, Recommendation
from app.schemas import RecommendRequest, RecommendResponse, RecommendationItem
from src.pipeline import RecommendationPipeline

router = APIRouter(tags=["recommendations"])

# Singleton pipeline instance loaded once
_pipeline = RecommendationPipeline(models_dir="models")


@router.post("/recommend", response_model=RecommendResponse)
def get_recommendations(req: RecommendRequest, db: Session = Depends(get_db)):
    """
    Takes an organization profile (or profile_id), runs the 2-stage candidate generation ->
    scoring -> re-ranking pipeline, returns ranked frameworks grouped by stage, each with
    a numeric score and short plain-language reason string.
    """
    profile_id = req.profile_id
    if profile_id is not None:
        db_profile = db.query(OrgProfile).filter(OrgProfile.id == profile_id).first()
        if not db_profile:
            raise HTTPException(status_code=404, detail="Organization profile not found")
        profile_data = db_profile
    else:
        # Check if industry is present in req
        if not req.industry:
            raise HTTPException(status_code=422, detail="Either profile_id or full organization profile fields are required")
        # Save or update inline profile
        profile_dict = req.to_profile_dict()
        db_profile = OrgProfile(**profile_dict)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        profile_id = db_profile.id
        profile_data = db_profile

    result = _pipeline.recommend(profile=profile_data, db=db, org_profile_id=profile_id)
    return result


@router.get("/recommendations/{profile_id}", response_model=list[RecommendationItem])
def get_past_recommendations(profile_id: int, db: Session = Depends(get_db)):
    """
    Fetch past recommendation history for an organization profile ID.
    """
    profile = db.query(OrgProfile).filter(OrgProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Organization profile not found")

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.org_profile_id == profile_id)
        .order_by(Recommendation.stage, Recommendation.score.desc())
        .all()
    )

    items = []
    for r in recs:
        items.append(RecommendationItem(
            id=r.id,
            framework_id=r.framework_id,
            slug=r.framework_slug,
            name=r.framework.name if r.framework else r.framework_slug,
            stage=r.stage,
            description=r.framework.description if r.framework else "",
            score=int(round(r.score)),
            reason=r.reason
        ))

    return items
