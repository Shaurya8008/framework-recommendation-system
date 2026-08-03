from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

def utcnow():
    return datetime.now(timezone.utc)


class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    short_name = Column(String(100), nullable=True)
    full_name = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    stage = Column(String(50), nullable=False, index=True)  # manage | measure | report | improve
    topic = Column(String(100), nullable=True)  # climate | energy | water | waste | governance | social | reporting | buildings | supply_chain | finance | circularity
    subtopic = Column(String(100), nullable=True)
    what_it_is = Column(Text, nullable=True)
    who_needs_it = Column(JSON, default=list)

    # Recommendation metadata
    geography_applicability = Column(JSON, default=list)  # global | india | eu | us | uk | sector_specific
    industry_fit = Column(JSON, default=list)  # array of industry slugs
    org_size_fit = Column(JSON, default=list)  # startup | sme | mid | enterprise
    mandatory_status = Column(String(50), default="voluntary")  # mandatory | quasi_mandatory | voluntary
    certifiable = Column(Boolean, default=False)
    output_type = Column(String(100), nullable=True)  # certification | standard | disclosure | target | commitment | rating | methodology
    prerequisites = Column(JSON, default=list)
    data_requirements = Column(JSON, default=list)
    maturity_min = Column(String(50), default="none")  # none | basic | intermediate | advanced
    maturity_max = Column(String(50), nullable=True)
    implementation_effort = Column(String(50), default="medium")  # low | medium | high
    assurance_relevance = Column(String(50), default="low")  # low | medium | high
    depends_on = Column(JSON, default=list)  # array of framework slugs
    recommended_next = Column(JSON, default=list)  # array of framework slugs
    priority_weight = Column(Float, default=1.0)
    recommendation_rule_notes = Column(Text, nullable=True)
    why_recommended_template = Column(Text, nullable=True)
    active = Column(Boolean, default=True, index=True)

    # Legacy compatibility
    region_applicability = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), default=utcnow)

    recommendations = relationship("Recommendation", back_populates="framework", cascade="all, delete-orphan")


class OrgProfile(Base):
    __tablename__ = "org_profiles"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(255), nullable=True, default="Your organization")
    industry = Column(String(100), nullable=False, index=True)
    subindustry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=False)  # legacy: 1-50, 50-250, etc.
    org_size = Column(String(50), nullable=True)  # startup | sme | mid | enterprise
    region = Column(String(50), nullable=False)
    is_listed = Column(Boolean, default=False)
    energy_use_level = Column(String(50), nullable=False)  # low | moderate | high | very-high
    annual_energy_use_level = Column(String(50), nullable=True)  # alias
    emissions_maturity = Column(String(50), nullable=False, default="none")  # none | basic | intermediate | advanced
    emissions_tracking_maturity = Column(String(50), nullable=True)  # alias
    certifications = Column(JSON, default=list)
    existing_certifications = Column(JSON, default=list)  # alias
    disclosure_level = Column(String(50), nullable=False, default="none")  # none | partial | full
    disclosure_obligations = Column(JSON, default=list)
    goals = Column(JSON, default=list)  # legacy
    sustainability_goals = Column(JSON, default=list)
    supply_chain_complexity = Column(String(50), default="low")  # low | medium | high
    export_exposure = Column(JSON, default=list)  # array of region slugs
    water_intensity = Column(String(50), default="low")  # low | medium | high
    waste_intensity = Column(String(50), default="low")  # low | medium | high
    facility_footprint = Column(String(50), default="single_site")  # single_site | multi_site
    investor_pressure = Column(String(50), default="low")  # low | medium | high
    customer_pressure = Column(String(50), default="low")  # low | medium | high
    assurance_readiness = Column(String(50), default="low")  # low | medium | high
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    recommendations = relationship("Recommendation", back_populates="org_profile", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    org_profile_id = Column(Integer, ForeignKey("org_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id", ondelete="CASCADE"), nullable=False, index=True)
    framework_slug = Column(String(100), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)  # legacy
    stage = Column(String(50), nullable=False, index=True)
    why_recommended = Column(Text, nullable=True)
    why_now = Column(Text, nullable=True)
    recommendation_type = Column(String(50), nullable=True)  # foundational | compliance | disclosure | target | advanced
    confidence_label = Column(String(50), nullable=True)  # high | medium | low
    missing_prerequisites = Column(JSON, default=list)
    recommended_next = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    org_profile = relationship("OrgProfile", back_populates="recommendations")
    framework = relationship("Framework", back_populates="recommendations")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    
    extractions = relationship("DocumentExtraction", back_populates="document", cascade="all, delete-orphan")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("org_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    
    field_name = Column(String(100), nullable=False)
    suggested_value = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=False)
    source_snippet = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    
    accepted_by_user = Column(Boolean, nullable=True)
    overridden_value = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)

    document = relationship("Document", back_populates="extractions")
    org_profile = relationship("OrgProfile")
