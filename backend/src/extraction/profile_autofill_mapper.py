from typing import List, Dict, Any
from app.schemas import AutofillFieldSuggestion

class ProfileAutofillMapper:
    @staticmethod
    def map_signals_to_suggestions(signals: Dict[str, Any]) -> List[AutofillFieldSuggestion]:
        suggestions = []

        # 1. Frameworks -> Disclosure Level / Region / Listing
        frameworks = signals.get("frameworks", [])
        if frameworks:
            framework_names = [f["framework"] for f in frameworks]
            
            # If they mention BRSR, likely India & Listed
            if "brsr" in framework_names:
                brsr_snippet = next((f["snippet"] for f in frameworks if f["framework"] == "brsr"), None)
                suggestions.append(AutofillFieldSuggestion(
                    field="region",
                    suggested_value="india",
                    confidence=0.85,
                    source_snippet=brsr_snippet,
                    reason="Mention of BRSR/SEBI strongly indicates India."
                ))
                suggestions.append(AutofillFieldSuggestion(
                    field="is_listed",
                    suggested_value=True,
                    confidence=0.8,
                    source_snippet=brsr_snippet,
                    reason="BRSR is primarily mandatory for listed entities in India."
                ))

            # Disclosure Level
            if any(f in framework_names for f in ["gri", "sasb", "tcfd", "csrd", "esrs"]):
                best_snippet = frameworks[0]["snippet"]
                suggestions.append(AutofillFieldSuggestion(
                    field="disclosure_level",
                    suggested_value="full",
                    confidence=0.75,
                    source_snippet=best_snippet,
                    reason="Mentions of major reporting frameworks suggest full public disclosure."
                ))

        # 2. Certifications
        certs = signals.get("certifications", [])
        if certs:
            cert_names = [c["cert"] for c in certs]
            snippet = certs[0]["snippet"]
            suggestions.append(AutofillFieldSuggestion(
                field="existing_certifications",
                suggested_value=cert_names,
                confidence=0.9,
                source_snippet=snippet,
                reason="Explicit mentions of ISO standards found."
            ))

            # Infer energy use from ISO 50001
            if "iso-50001" in cert_names:
                suggestions.append(AutofillFieldSuggestion(
                    field="annual_energy_use_level",
                    suggested_value="high",
                    confidence=0.7,
                    source_snippet=snippet,
                    reason="ISO 50001 certification often correlates with high energy usage."
                ))

        # 3. Emissions Maturity
        emissions = signals.get("emissions")
        if emissions:
            maturity = "basic"
            reason = "Mention of Scope 1/2 emissions."
            if emissions.get("scope_3"):
                maturity = "advanced"
                reason = "Mention of Scope 3 emissions indicates advanced tracking."
            
            suggestions.append(AutofillFieldSuggestion(
                field="emissions_tracking_maturity",
                suggested_value=maturity,
                confidence=0.8,
                source_snippet=emissions.get("snippet"),
                reason=reason
            ))

        # 4. Energy Level
        energy = signals.get("energy")
        if energy and not any(s.field == "annual_energy_use_level" for s in suggestions):
            suggestions.append(AutofillFieldSuggestion(
                field="annual_energy_use_level",
                suggested_value="moderate",
                confidence=0.5,
                source_snippet=energy.get("snippet"),
                reason="Energy consumption data mentioned."
            ))

        # 5. Goals
        goals = signals.get("goals", [])
        if goals:
            goal_names = [g["goal"] for g in goals]
            snippet = goals[0]["snippet"]
            suggestions.append(AutofillFieldSuggestion(
                field="sustainability_goals",
                suggested_value=goal_names,
                confidence=0.85,
                source_snippet=snippet,
                reason="Explicit sustainability goals mentioned."
            ))

        # 6. Operations / Industry
        ops = signals.get("operations")
        if ops and ops.get("type") == "manufacturing":
            suggestions.append(AutofillFieldSuggestion(
                field="industry",
                suggested_value="manufacturing",
                confidence=0.75,
                source_snippet=ops.get("snippet"),
                reason="Mention of manufacturing facilities."
            ))
            suggestions.append(AutofillFieldSuggestion(
                field="facility_footprint",
                suggested_value="multi_site",
                confidence=0.7,
                source_snippet=ops.get("snippet"),
                reason="Plural references to plants/factories."
            ))

        # 7. Supply Chain
        supply = signals.get("supply_chain")
        if supply:
            suggestions.append(AutofillFieldSuggestion(
                field="supply_chain_complexity",
                suggested_value="high",
                confidence=0.65,
                source_snippet=supply.get("snippet"),
                reason="References to supplier audits or complex procurement."
            ))

        # 8. Assurance
        assurance = signals.get("assurance")
        if assurance:
            suggestions.append(AutofillFieldSuggestion(
                field="assurance_readiness",
                suggested_value="high",
                confidence=0.8,
                source_snippet=assurance.get("snippet"),
                reason="Direct mention of external assurance."
            ))

        return suggestions
