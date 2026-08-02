from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator

class FrameworkRead(BaseModel):
    id: int
    slug: str
    name: str
    full_name: str
    stage: str
    description: str
    what_it_is: Optional[str] = None
    who_needs_it: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    region_applicability: list[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class OrgProfileBase(BaseModel):
    organization_name: Optional[str] = Field(default="Your organization", alias="organizationName")
    industry: str
    size: str
    region: str
    energy_use_level: str
    emissions_maturity: str = "none"
    certifications: list[str] = Field(default_factory=list)
    disclosure_level: str = "none"
    goals: list[str] = Field(default_factory=list)

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


class RecommendationItem(BaseModel):
    id: Optional[int] = None
    framework_id: Optional[int] = None
    slug: str
    name: str
    stage: str
    description: str
    score: int
    reason: str

    class Config:
        from_attributes = True


class RecommendResponse(BaseModel):
    profileSummary: str
    stages: dict[str, list[RecommendationItem]]


class RecommendRequest(BaseModel):
    profile_id: Optional[int] = None
    id: Optional[int] = None
    organization_name: Optional[str] = Field(default=None, alias="organizationName")
    industry: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    energy_use_level: Optional[str] = None
    energyUse: Optional[str] = None
    emissions_maturity: Optional[str] = None
    certifications: Optional[list[str]] = None
    disclosure_level: Optional[str] = None
    disclosure: Optional[str] = None
    goals: Optional[list[str]] = None

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
        return data

    def to_profile_dict(self) -> dict[str, Any]:
        return {
            "organization_name": self.organization_name or "Your organization",
            "industry": self.industry or "manufacturing",
            "size": self.size or "250-1000",
            "region": self.region or "global",
            "energy_use_level": self.energy_use_level or self.energyUse or "moderate",
            "emissions_maturity": self.emissions_maturity or "none",
            "certifications": self.certifications or [],
            "disclosure_level": self.disclosure_level or self.disclosure or "none",
            "goals": self.goals or []
        }

    class Config:
        populate_by_name = True
