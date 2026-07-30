from typing import Any, Optional
from sqlalchemy.orm import Session
from src.candidates import generate_candidates, _get_val
from src.model import ScoringEngine
from src.rerank import rerank_recommendations
from app.db.models import Framework, Recommendation


class RecommendationPipeline:
    """
    End-to-end 3-Stage Recommendation Pipeline:
    Stage 1: Candidate Generation (shortlist relevant frameworks by stage and region)
    Stage 2: Scoring Model (v2 stage classifier + v3 ranker, with v1 rule-based fallback)
    Stage 3: Business Logic Re-ranking (Manage -> Measure -> Report -> Improve prerequisite order)
    """
    def __init__(self, models_dir: str = "models"):
        self.scoring_engine = ScoringEngine(models_dir=models_dir)

    def recommend(
        self,
        profile: Any,
        db: Optional[Session] = None,
        org_profile_id: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Executes the recommendation pipeline for an organization profile.
        Returns a dict matching the UI schema:
        {
            "profileSummary": string,
            "stages": { "manage": [...], "measure": [...], "report": [...], "improve": [...] }
        }
        Optionally persists recommendation history to database if db and org_profile_id are provided.
        """
        # 0. Load framework catalog
        if db is not None:
            catalog = db.query(Framework).all()
        else:
            from app.db.seed import INITIAL_FRAMEWORKS
            catalog = INITIAL_FRAMEWORKS

        # 1. Candidate Generation
        shortlist = generate_candidates(profile, catalog)

        # 2. Scoring (ML v2/v3 or Rule-based v1 fallback)
        scored_candidates = self.scoring_engine.score_candidates(profile, shortlist)

        # 3. Re-ranking
        stages_dict = rerank_recommendations(scored_candidates, profile)

        # 4. Generate profile summary string matching UI expectation
        org_name = _get_val(profile, "organization_name", "") or _get_val(profile, "organizationName", "") or "Your organization"
        industry = _get_val(profile, "industry", "")
        size = _get_val(profile, "size", "")
        region = _get_val(profile, "region", "")

        parts = [org_name]
        if industry:
            parts.append(f"· {industry.replace('-', ' ')}")
        if size:
            parts.append(f"· {size} employees")
        if region:
            parts.append(f"· {region.upper()}")
        profile_summary = " ".join(parts)

        # 5. Persist recommendations to DB if session provided
        if db is not None and org_profile_id is not None:
            try:
                # Delete old recommendations for this profile if re-running
                db.query(Recommendation).filter_by(org_profile_id=org_profile_id).delete()
                for stage_id, items in stages_dict.items():
                    for item in items:
                        f_id = item.get("id") or item.get("framework_id")
                        if f_id is None:
                            # Look up ID by slug
                            f_obj = db.query(Framework).filter_by(slug=item["slug"]).first()
                            f_id = f_obj.id if f_obj else 1
                        rec = Recommendation(
                            org_profile_id=org_profile_id,
                            framework_id=f_id,
                            framework_slug=item["slug"],
                            score=float(item["score"]),
                            reason=item["reason"],
                            stage=stage_id
                        )
                        db.add(rec)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Warning: Failed to persist recommendations to DB: {e}")

        return {
            "profileSummary": profile_summary,
            "stages": stages_dict
        }
