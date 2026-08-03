"""
Unified recommendation pipeline — V2.

Orchestrates the full recommendation flow:
1. Normalize profile
2. Generate candidates (high-recall)
3. Score candidates (transparent weighted scoring)
4. Generate explanations
5. Re-rank with business logic
6. Build response (grouped by stage, top recommendations, missing foundations)
7. Persist to DB

Architected so ML scoring can replace or augment the rule-based scoring
in step 3 by swapping the score_all_candidates function.
"""

from __future__ import annotations
from typing import Any, Optional
from sqlalchemy.orm import Session

from src.normalize_profile import normalize_profile, NormalizedProfile
from src.candidate_generation import generate_candidates
from src.scoring import score_all_candidates, SCORING_WEIGHTS
from src.explainability import generate_explanations
from src.reranking import rerank, STAGE_ORDER
from app.db.models import Framework, Recommendation


class RecommendationPipeline:
    """
    End-to-end recommendation pipeline — V2.

    Stages:
    1. Profile Normalization
    2. Candidate Generation (broad high-recall filter)
    3. Scoring (transparent weighted rules)
    4. Explainability (per-item reasons)
    5. Business Logic Re-ranking (Manage → Measure → Report → Improve)
    6. Response Assembly
    7. DB Persistence
    """

    def __init__(self, models_dir: str = "models"):
        # models_dir kept for future ML model loading
        self.models_dir = models_dir

    def recommend(
        self,
        profile: Any,
        db: Optional[Session] = None,
        org_profile_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Execute the full recommendation pipeline.

        Returns the enriched response dict matching RecommendResponse schema.
        """
        # 0. Load framework catalog
        if db is not None:
            catalog = db.query(Framework).filter(Framework.active == True).all()
        else:
            from app.db.seed import INITIAL_FRAMEWORKS
            catalog = INITIAL_FRAMEWORKS

        # 1. Normalize profile
        normalized = normalize_profile(profile)

        # 2. Generate candidates
        candidates = generate_candidates(normalized, catalog)

        # 3. Score candidates
        scored = score_all_candidates(normalized, candidates)

        # 4. Generate explanations
        explained = generate_explanations(normalized, scored)

        # 5. Re-rank
        grouped = rerank(explained, normalized)

        # 6. Build response
        response = self._build_response(normalized, grouped, len(candidates), len(scored), org_profile_id)

        # 7. Persist to DB
        if db is not None and org_profile_id is not None:
            self._persist_recommendations(db, org_profile_id, grouped)

        return response

    def _build_response(
        self,
        profile: NormalizedProfile,
        grouped: dict[str, list[dict[str, Any]]],
        total_candidates: int,
        total_scored: int,
        profile_id: Optional[int],
    ) -> dict[str, Any]:
        """Assemble the final response payload."""

        # Profile summary string
        parts = [profile.organization_name]
        if profile.industry:
            parts.append(f"· {profile.industry.replace('-', ' ')}")
        if profile.org_size:
            parts.append(f"· {profile.org_size}")
        if profile.region:
            parts.append(f"· {profile.region.upper()}")
        profile_summary = " ".join(parts)

        # Overall top recommendations (top 5 across all stages)
        all_items: list[dict[str, Any]] = []
        for stage in STAGE_ORDER:
            all_items.extend(grouped.get(stage, []))
        all_items.sort(key=lambda x: x.get("score", 0), reverse=True)
        top_recommendations = self._to_recommendation_items(all_items[:5])

        # Grouped by stage
        grouped_items: dict[str, list[dict[str, Any]]] = {}
        for stage in STAGE_ORDER:
            grouped_items[stage] = self._to_recommendation_items(grouped.get(stage, []))

        # Missing foundations
        missing_foundations = self._find_missing_foundations(profile, grouped)

        # Next best step
        next_step = self._determine_next_step(profile, grouped)

        # Scoring metadata
        scoring_metadata = {
            "total_candidates": total_candidates,
            "total_scored": total_scored,
            "scoring_version": "v1_rule_based",
            "weights_used": SCORING_WEIGHTS,
        }

        return {
            "profile_id": profile_id,
            "summary": profile_summary,
            "profileSummary": profile_summary,  # legacy alias
            "overall_top_recommendations": top_recommendations,
            "grouped_recommendations_by_stage": grouped_items,
            "stages": grouped_items,  # legacy alias
            "missing_foundations": missing_foundations,
            "next_best_step": next_step,
            "scoring_metadata": scoring_metadata,
        }

    def _to_recommendation_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert internal scored dicts to RecommendationItem-compatible dicts."""
        results = []
        for item in items:
            results.append({
                "id": item.get("id"),
                "framework_id": item.get("framework_id"),
                "slug": item.get("slug", ""),
                "name": item.get("name", ""),
                "stage": item.get("stage", ""),
                "description": item.get("description", ""),
                "score": item.get("score", 0),
                "reason": item.get("reason", item.get("why_recommended", "")),
                "why_recommended": item.get("why_recommended", ""),
                "why_now": item.get("why_now", ""),
                "prerequisites": item.get("prerequisites", []),
                "missing_prerequisites": item.get("missing_prerequisites", []),
                "depends_on": item.get("depends_on", []),
                "recommended_next": item.get("recommended_next", []),
                "recommendation_type": item.get("recommendation_type", "foundational"),
                "confidence_label": item.get("confidence_label", "medium"),
            })
        return results

    def _find_missing_foundations(
        self,
        profile: NormalizedProfile,
        grouped: dict[str, list[dict[str, Any]]],
    ) -> list[str]:
        """Identify foundational gaps the organization should address."""
        missing: list[str] = []
        certs = set(profile.existing_certifications)

        if not certs & {"iso-14001"}:
            missing.append("No environmental management system (ISO 14001) in place")
        if profile.emissions_tracking_maturity == "none":
            missing.append("No emissions inventory — GHG Protocol Corporate Standard is the essential first step")
        if profile.is_listed and profile.region == "india" and "brsr" not in certs:
            missing.append("BRSR disclosure is mandatory for listed Indian companies")
        if (profile.region == "eu" or "eu" in profile.export_exposure):
            missing.append("CSRD/ESRS readiness should be assessed for EU-scope operations")

        return missing

    def _determine_next_step(
        self,
        profile: NormalizedProfile,
        grouped: dict[str, list[dict[str, Any]]],
    ) -> str:
        """Determine the single most important next step."""
        if profile.emissions_tracking_maturity == "none":
            return "Start with the GHG Protocol Corporate Standard to establish your emissions baseline — every reporting and target framework depends on this."

        certs = set(profile.existing_certifications)
        if not certs & {"iso-14001"}:
            return "Adopt ISO 14001 to establish the environmental management governance foundation that later frameworks assume."

        if profile.is_listed and profile.region == "india":
            return "Prioritize BRSR alignment — it is SEBI-mandated and your most pressing compliance obligation."

        if profile.region == "eu" or "eu" in profile.export_exposure:
            return "Begin CSRD/ESRS gap analysis — mandatory reporting deadlines require the longest preparation time."

        # Default: recommend the highest-scored item
        for stage in STAGE_ORDER:
            items = grouped.get(stage, [])
            if items:
                top = items[0]
                return f"Focus on {top.get('name', '')} ({top.get('stage', '').upper()} stage) — {top.get('why_now', 'it aligns with your current readiness.')}."

        return "Review the recommended frameworks and begin with the highest-scored foundational items."

    def _persist_recommendations(
        self,
        db: Session,
        org_profile_id: int,
        grouped: dict[str, list[dict[str, Any]]],
    ) -> None:
        """Persist recommendation results to database."""
        try:
            # Delete old recommendations for this profile
            db.query(Recommendation).filter_by(org_profile_id=org_profile_id).delete()

            for stage_id, items in grouped.items():
                for item in items:
                    f_id = item.get("id") or item.get("framework_id")
                    if f_id is None:
                        f_obj = db.query(Framework).filter_by(slug=item.get("slug", "")).first()
                        f_id = f_obj.id if f_obj else 1

                    rec = Recommendation(
                        org_profile_id=org_profile_id,
                        framework_id=f_id,
                        framework_slug=item.get("slug", ""),
                        score=float(item.get("score", 0)),
                        reason=item.get("reason", item.get("why_recommended", "")),
                        stage=stage_id,
                        why_recommended=item.get("why_recommended", ""),
                        why_now=item.get("why_now", ""),
                        recommendation_type=item.get("recommendation_type", "foundational"),
                        confidence_label=item.get("confidence_label", "medium"),
                        missing_prerequisites=item.get("missing_prerequisites", []),
                        recommended_next=item.get("recommended_next", []),
                    )
                    db.add(rec)

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to persist recommendations to DB: {e}")
