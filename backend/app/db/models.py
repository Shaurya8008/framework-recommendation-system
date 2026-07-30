from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    full_name = Column(String(300), nullable=False)
    stage = Column(String(50), nullable=False, index=True)  # manage, measure, report, improve
    description = Column(Text, nullable=False)
    what_it_is = Column(Text, nullable=True)
    who_needs_it = Column(JSON, default=list)
    prerequisites = Column(JSON, default=list)
    region_applicability = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    recommendations = relationship("Recommendation", back_populates="framework", cascade="all, delete-orphan")


class OrgProfile(Base):
    __tablename__ = "org_profiles"

    id = Column(Integer, primary_key=True, index=True)
    organization_name = Column(String(255), nullable=True, default="Your organization")
    industry = Column(String(100), nullable=False, index=True)
    size = Column(String(50), nullable=False)
    region = Column(String(50), nullable=False)
    energy_use_level = Column(String(50), nullable=False)  # low, moderate, high, very-high
    emissions_maturity = Column(String(50), nullable=False)  # none, basic, advanced
    certifications = Column(JSON, default=list)
    disclosure_level = Column(String(50), nullable=False)  # none, partial, full
    goals = Column(JSON, default=list)
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
    reason = Column(Text, nullable=False)
    stage = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    org_profile = relationship("OrgProfile", back_populates="recommendations")
    framework = relationship("Framework", back_populates="recommendations")
