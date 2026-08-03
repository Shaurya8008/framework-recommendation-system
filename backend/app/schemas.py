from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Framework schemas
# ---------------------------------------------------------------------------

class FrameworkRead(BaseModel):
    id: int
    slug: str
    name: str
    short_name: Optional[str] = None
    full_name: str
    stage: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    description: str
    what_it_is: Optional[str] = None
    who_needs_it: list[str] = Field(default_factory=list)
    geography_applicability: list[str] = Field(default_factory=list)
    industry_fit: list[str] = Field(default_factory=list)
    org_size_fit: list[str] = Field(default_factory=list)
    mandatory_status: str = "voluntary"
    certifiable: bool = False
    output_type: Optional[str] = None
    prerequisites: list[str] = Field(default_factory=list)
    data_requirements: list[str] = Field(default_factory=list)
    maturity_min: str = "none"
    maturity_max: Optional[str] = None
    implementation_effort: str = "medium"
    assurance_relevance: str = "low"
    depends_on: list[str] = Field(default_factory=list)
    recommended_next: list[str] = Field(default_factory=list)
    priority_weight: float = 1.0
    recommendation_rule_notes: Optional[str] = None
    why_recommended_template: Optional[str] = None
    active: bool = True
    region_applicability: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Organization profile schemas
# ---------------------------------------------------------------------------

class OrgProfileBase(BaseModel):
    organization_name: Optional[str] = Field(default="Your organization", alias="organizationName")
    industry: str
    subindustry: Optional[str] = None
    size: str = "250-1000"
    org_size: Optional[str] = None  # startup | sme | mid | enterprise
    region: str
    is_listed: bool = False
    energy_use_level: str = "moderate"
    annual_energy_use_level: Optional[str] = None
    emissions_maturity: str = "none"
    emissions_tracking_maturity: Optional[str] = None
    certifications: list[str] = Field(default_factory=list)
    existing_certifications: list[str] = Field(default_factory=list)
    disclosure_level: str = "none"
    disclosure_obligations: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    sustainability_goals: list[str] = Field(default_factory=list)
    supply_chain_complexity: str = "low"
    export_exposure: list[str] = Field(default_factory=list)
    water_intensity: str = "low"
    waste_intensity: str = "low"
    facility_footprint: str = "single_site"
    investor_pressure: str = "low"
    customer_pressure: str = "low"
    assurance_readiness: str = "low"

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Support camelCase and short names from frontend
            if "organizationName" in data and "organization_name" not in data:
                data["organization_name"] = data["organizationName"]
            if "energyUse" in data and "energy_use_level" not in data:
                data["energy_use_level"] = data["energyUse"]
            if "disclosure" in data and "disclosure_level" not in data:
                data["disclosure_level"] = data["disclosure"]
            # Sync alias fields
            if "annual_energy_use_level" in data and "energy_use_level" not in data:
                data["energy_use_level"] = data["annual_energy_use_level"]
            if "emissions_tracking_maturity" in data and "emissions_maturity" not in data:
                data["emissions_maturity"] = data["emissions_tracking_maturity"]
            if "existing_certifications" in data and "certifications" not in data:
                data["certifications"] = data["existing_certifications"]
            if "sustainability_goals" in data and "goals" not in data:
                data["goals"] = data["sustainability_goals"]
        return data

    class Config:
        populate_by_name = True
        from_attributes = True


class OrgProfileCreate(OrgProfileBase):
    pass


class OrgProfileRead(OrgProfileBase):
    id: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Recommendation schemas
# ---------------------------------------------------------------------------

class RecommendationItem(BaseModel):
    id: Optional[int] = None
    framework_id: Optional[int] = None
    slug: str
    name: str
    stage: str
    description: str
    score: float
    reason: str  # legacy — kept for backward compatibility
    why_recommended: str = ""
    why_now: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    missing_prerequisites: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    recommended_next: list[str] = Field(default_factory=list)
    recommendation_type: str = "foundational"  # foundational | compliance | disclosure | target | advanced
    confidence_label: str = "medium"  # high | medium | low

    class Config:
        from_attributes = True


class ScoringMetadata(BaseModel):
    total_candidates: int = 0
    total_scored: int = 0
    scoring_version: str = "v1_rule_based"
    weights_used: dict[str, float] = Field(default_factory=dict)


class RecommendResponse(BaseModel):
    profile_id: Optional[int] = None
    summary: str = ""
    profileSummary: str = ""  # legacy alias
    overall_top_recommendations: list[RecommendationItem] = Field(default_factory=list)
    grouped_recommendations_by_stage: dict[str, list[RecommendationItem]] = Field(default_factory=dict)
    stages: dict[str, list[RecommendationItem]] = Field(default_factory=dict)  # legacy alias
    missing_foundations: list[str] = Field(default_factory=list)
    next_best_step: str = ""
    scoring_metadata: Optional[ScoringMetadata] = None


class RecommendRequest(BaseModel):
    profile_id: Optional[int] = None
    id: Optional[int] = None
    organization_name: Optional[str] = Field(default=None, alias="organizationName")
    industry: Optional[str] = None
    subindustry: Optional[str] = None
    size: Optional[str] = None
    org_size: Optional[str] = None
    region: Optional[str] = None
    is_listed: Optional[bool] = None
    energy_use_level: Optional[str] = None
    energyUse: Optional[str] = None
    annual_energy_use_level: Optional[str] = None
    emissions_maturity: Optional[str] = None
    emissions_tracking_maturity: Optional[str] = None
    certifications: Optional[list[str]] = None
    existing_certifications: Optional[list[str]] = None
    disclosure_level: Optional[str] = None
    disclosure: Optional[str] = None
    disclosure_obligations: Optional[list[str]] = None
    goals: Optional[list[str]] = None
    sustainability_goals: Optional[list[str]] = None
    supply_chain_complexity: Optional[str] = None
    export_exposure: Optional[list[str]] = None
    water_intensity: Optional[str] = None
    waste_intensity: Optional[str] = None
    facility_footprint: Optional[str] = None
    investor_pressure: Optional[str] = None
    customer_pressure: Optional[str] = None
    assurance_readiness: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "organizationName" in data and "organization_name" not in data:
                data["organization_name"] = data.get("organizationName")
            if "energyUse" in data and "energy_use_level" not in data:
                data["energy_use_level"] = data.get("energyUse")
            if "emissionsMaturity" in data and "emissions_maturity" not in data:
                data["emissions_maturity"] = data.get("emissionsMaturity")
            if "disclosure" in data and "disclosure_level" not in data:
                data["disclosure_level"] = data.get("disclosure")
            if "id" in data and "profile_id" not in data:
                data["profile_id"] = data.get("id")
            if "annual_energy_use_level" in data and "energy_use_level" not in data:
                data["energy_use_level"] = data["annual_energy_use_level"]
            if "emissions_tracking_maturity" in data and "emissions_maturity" not in data:
                data["emissions_maturity"] = data["emissions_tracking_maturity"]
            if "existing_certifications" in data and "certifications" not in data:
                data["certifications"] = data["existing_certifications"]
            if "sustainability_goals" in data and "goals" not in data:
                data["goals"] = data["sustainability_goals"]
        return data

    def to_profile_dict(self) -> dict[str, Any]:
        return {
            "organization_name": self.organization_name or "Your organization",
            "industry": self.industry or "manufacturing",
            "subindustry": self.subindustry,
            "size": self.size or "250-1000",
            "org_size": self.org_size,
            "region": self.region or "global",
            "is_listed": self.is_listed or False,
            "energy_use_level": self.energy_use_level or self.energyUse or self.annual_energy_use_level or "moderate",
            "annual_energy_use_level": self.annual_energy_use_level or self.energy_use_level or self.energyUse or "moderate",
            "emissions_maturity": self.emissions_maturity or self.emissions_tracking_maturity or "none",
            "emissions_tracking_maturity": self.emissions_tracking_maturity or self.emissions_maturity or "none",
            "certifications": self.certifications or self.existing_certifications or [],
            "existing_certifications": self.existing_certifications or self.certifications or [],
            "disclosure_level": self.disclosure_level or self.disclosure or "none",
            "disclosure_obligations": self.disclosure_obligations or [],
            "goals": self.goals or self.sustainability_goals or [],
            "sustainability_goals": self.sustainability_goals or self.goals or [],
            "supply_chain_complexity": self.supply_chain_complexity or "low",
            "export_exposure": self.export_exposure or [],
            "water_intensity": self.water_intensity or "low",
            "waste_intensity": self.waste_intensity or "low",
            "facility_footprint": self.facility_footprint or "single_site",
            "investor_pressure": self.investor_pressure or "low",
            "customer_pressure": self.customer_pressure or "low",
            "assurance_readiness": self.assurance_readiness or "low",
        }

    class Config:
        populate_by_name = True

# ---------------------------------------------------------------------------
# Autofill schemas
# ---------------------------------------------------------------------------

class AutofillFieldSuggestion(BaseModel):
    field: str
    suggested_value: Any
    confidence: float
    source: str = "document"
    source_snippet: Optional[str] = None
    reason: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: int
    status: str
    overall_confidence: float
    suggestions: list[AutofillFieldSuggestion] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)

