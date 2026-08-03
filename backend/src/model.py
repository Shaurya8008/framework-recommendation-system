import os
from typing import Any
import joblib
import numpy as np
import pandas as pd
from src.features import extract_features_dataframe, _get_val

HEAVY_INDUSTRIES = ["manufacturing", "energy", "chemicals", "construction", "transport"]

class RuleBasedScorer:
    """
    v1 Rule-based scoring engine for sustainability frameworks.
    Produces accurate baseline numeric scores [10..99] and plain-language explainable reasons.
    """
    @staticmethod
    def score(profile: Any, framework: Any) -> tuple[int, str]:
        slug = _get_val(framework, "slug", "")
        name = _get_val(framework, "name", slug)
        stage = _get_val(framework, "stage", "manage")

        certifications = set(_get_val(profile, "certifications", []) or [])
        goals = set(_get_val(profile, "goals", []) or [])
        industry = _get_val(profile, "industry", "manufacturing")
        size = _get_val(profile, "size", "250-1000")
        region = _get_val(profile, "region", "global")
        energy_use = _get_val(profile, "energy_use_level", "moderate") or _get_val(profile, "energyUse", "moderate")
        emissions_maturity = _get_val(profile, "emissions_maturity", "none")
        disclosure = _get_val(profile, "disclosure_level", "none") or _get_val(profile, "disclosure", "none")

        heavy = industry in HEAVY_INDUSTRIES
        high_energy = energy_use in ["high", "very-high"]
        large = size in ["1000-5000", "5000+"]
        eu = (region == "eu")
        india = (region == "india")

        certified = lambda s: s in certifications
        goal = lambda g: g in goals

        if slug == "iso-14001":
            if not certified("iso-14001"):
                score = 60 + (25 if heavy else 8) + (6 if large else 0)
                reason = f"You have no ISO 14001 certification yet{' and ' + industry + ' operations carry site-level environmental impacts' if heavy else ''}. An EMS gives you the governance backbone every later framework assumes."
                return min(99, max(10, score)), reason
            else:
                return 40, "You hold ISO 14001 certification; maintain audits and use it to underpin your GHG and reporting workflows."

        elif slug == "iso-50001":
            if not certified("iso-50001") and high_energy:
                score = 72 + (12 if heavy else 0)
                reason = f"You reported {energy_use.replace('-', ' ')} energy use, so energy is a material cost and emissions driver. ISO 50001 turns that into measured, managed reduction."
                return min(99, max(10, score)), reason
            elif certified("iso-50001"):
                return 45, "You already hold ISO 50001; integrate energy performance indicators into your GHG inventory."
            else:
                return 35, "ISO 50001 can help optimize operational energy performance."

        elif slug == "iso-45001":
            if not certified("iso-45001") and heavy:
                return 52, "Operational, plant-based work usually means occupational risk. ISO 45001 shares its structure with ISO 14001, so audits can be integrated."
            return 30, "Occupational health and safety standard integrating with environmental governance."

        elif slug == "ghg-protocol-corporate":
            if emissions_maturity == "none":
                return 96, "You are not tracking emissions yet. The GHG Protocol is the starting point — every reporting and target framework depends on this inventory."
            elif emissions_maturity == "basic":
                return 88, "Your tracking is basic. Extending to full Scope 3 coverage under the GHG Protocol unlocks disclosure and target setting."
            else:
                return 70, "Your inventory is advanced; keep it aligned to the GHG Protocol as your reference methodology for all disclosures."

        elif slug == "iso-14064-1":
            if emissions_maturity != "none" and (large or disclosure != "none"):
                score = 64 + (10 if large else 0)
                return min(99, max(10, score)), f"With {('public disclosure in play' if disclosure != 'none' else 'an established inventory')}, third-party verification protects your numbers under scrutiny and assurance requirements."
            return 45, "Standard for GHG quantification and independent verification."

        elif slug == "iso-14040":
            if heavy or industry in ["consumer-goods", "agriculture"]:
                return 58, f"{industry.replace('-', ' ').title()} companies face product-level footprint requests from customers and retailers; LCA is the accepted method."
            return 35, "Assesses product-level environmental footprint across the full life cycle."

        elif slug == "csrd":
            if eu:
                return 92, "Your EU footprint puts CSRD/ESRS in scope or near-scope. It is mandatory, assured, and requires double materiality — the longest lead time of anything here."
            elif large:
                return 62, "At your size, CSRD can reach you indirectly through EU customers and subsidiaries. Early ESRS gap analysis is cheap insurance."
            return 40, "EU reporting directive requiring double materiality and assured ESG disclosure."

        elif slug == "brsr":
            if india:
                return 90, "For Indian entities, BRSR is the SEBI-prescribed format and BRSR Core attributes require reasonable assurance — align your data collection to it first."
            return 30, "SEBI-prescribed sustainability reporting framework for Indian entities."

        elif slug == "ifrs-s1":
            if large:
                return 82, "Investor-facing entities of your size are the primary audience for IFRS S1/S2, which is becoming the global disclosure baseline."
            return 58, "ISSB is worth tracking now so your data structure does not need rebuilding when it applies to you."

        elif slug == "tcfd":
            if disclosure == "none":
                return 68, "TCFD's four pillars are the simplest on-ramp to climate risk disclosure and map directly into IFRS S2 later."
            return 74, "TCFD climate risk structure is widely expected by lenders and investors and feeds into IFRS S2."

        elif slug == "gri":
            if disclosure != "none" or goal("stakeholder-trust"):
                score = 78 if disclosure == "full" else 66
                return score, f"You already report {('publicly and fully' if disclosure == 'full' else 'partially')}, so GRI gives that report a recognised, impact-materiality structure."
            return 55, "GRI Standards offer a comprehensive multi-stakeholder sustainability reporting baseline."

        elif slug == "cdp-climate":
            if large or disclosure == "full":
                return 60, "Large buyers and investors commonly cascade CDP questionnaires; a scored response is often a procurement prerequisite."
            return 45, "Annual scored questionnaire widely used by procurement teams and investors."

        elif slug == "sbti":
            if goal("net_zero") or goal("sbti"):
                return 94, "You selected science-based / net-zero ambitions. SBTi validation is what turns that ambition into a defensible, externally checked target."
            return 50, "SBTi validates near-term and net-zero emissions reduction targets against 1.5°C pathways."

        elif slug == "net-zero-standard":
            if goal("net_zero") or goal("sbti"):
                return 80, "A net-zero claim needs ~90% deep decarbonisation before neutralisation. This standard defines what you must be able to evidence."
            return 45, "Defines rules for credible corporate net-zero claims."

        elif slug == "sdgs":
            if goal("sdg"):
                return 70, "You want SDG alignment. Map material activities to specific SDG targets and indicators rather than claiming whole goals."
            return 50, "Shared 17-goal language for framing sustainability strategy and positive impact."

        elif slug == "re100":
            if goal("renewables") or high_energy:
                score = 76 if high_energy else 62
                reason = "High electricity consumption means Scope 2 is likely your fastest reduction lever — a sourcing roadmap converts it into a plan." if high_energy else "You flagged renewable sourcing as a goal; a staged PPA and certificate roadmap makes it auditable."
                return score, reason
            return 45, "Staged plan to shift purchased electricity to renewable sources."

        # Default fallback score
        return 45, f"{name} provides valuable guidance for the {stage.upper()} stage of your sustainability journey."


class ScoringEngine:
    """
    Unified scoring engine that attempts to load trained ML models (v2 Stage Classifier
    and v3 Framework Ranker) from models/ directory, falling back to v1 RuleBasedScorer
    if ML models are missing or fail.
    """
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.v2_classifier = None
        self.v3_ranker = None
        self.ml_loaded = False
        self._load_models()

    def _load_models(self):
        v2_path = os.path.join(self.models_dir, "v2_stage_classifier.joblib")
        v3_path = os.path.join(self.models_dir, "v3_framework_ranker.joblib")
        if os.path.exists(v2_path) and os.path.exists(v3_path):
            try:
                self.v2_classifier = joblib.load(v2_path)
                self.v3_ranker = joblib.load(v3_path)
                self.ml_loaded = True
            except Exception as e:
                print(f"Warning: Failed to load ML models ({e}), falling back to v1 rule-based scoring.")
                self.ml_loaded = False
        else:
            self.ml_loaded = False

    def score_candidates(self, profile: Any, candidates: list[Any]) -> list[dict[str, Any]]:
        """
        Scores a list of candidate frameworks for an organization profile.
        Returns a list of dicts with keys: id, framework_id, slug, name, stage, description, score, reason.
        """
        results = []

        if self.ml_loaded and self.v2_classifier is not None and self.v3_ranker is not None:
            try:
                # ML-based scoring (v2 stage classifier + v3 ranker)
                profile_df = extract_features_dataframe([profile])
                stage_probs = self.v2_classifier.predict_proba(profile_df)[0]
                stage_classes = self.v2_classifier.classes_
                prob_map = {cls: float(prob) for cls, prob in zip(stage_classes, stage_probs)}

                for f in candidates:
                    slug = _get_val(f, "slug", "")
                    name = _get_val(f, "name", slug)
                    stage = _get_val(f, "stage", "manage")
                    description = _get_val(f, "description", "")
                    f_id = _get_val(f, "id", None)

                    # Stage relevance multiplier from v2 probability
                    stage_mult = prob_map.get(stage, 0.25) * 4.0

                    # Ranker score from v3
                    f_row = profile_df.copy()
                    f_row["framework_slug_hash"] = hash(slug) % 1000
                    base_score = float(self.v3_ranker.predict(f_row)[0])
                    ml_score = int(np.clip(round(base_score * (0.8 + 0.2 * stage_mult)), 10, 99))

                    # Use rule-based reason generation for plain-language interpretability
                    _, reason = RuleBasedScorer.score(profile, f)

                    results.append({
                        "id": f_id,
                        "framework_id": f_id,
                        "slug": slug,
                        "name": name,
                        "stage": stage,
                        "description": description,
                        "score": ml_score,
                        "reason": reason
                    })
                return results
            except Exception as e:
                print(f"ML scoring failed ({e}), falling back to v1 RuleBasedScorer.")

        # Fallback to v1 rule-based scoring
        for f in candidates:
            slug = _get_val(f, "slug", "")
            name = _get_val(f, "name", slug)
            stage = _get_val(f, "stage", "manage")
            description = _get_val(f, "description", "")
            f_id = _get_val(f, "id", None)

            score, reason = RuleBasedScorer.score(profile, f)
            results.append({
                "id": f_id,
                "framework_id": f_id,
                "slug": slug,
                "name": name,
                "stage": stage,
                "description": description,
                "score": score,
                "reason": reason
            })
        return results
