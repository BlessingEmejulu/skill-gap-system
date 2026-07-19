"""
Skill: the master taxonomy of skills used by both graduates and job postings.
SkillGap: a computed record of which required skills a graduate is missing for a given job.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin, SkillCategory


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False, index=True)
    category = Column(Enum(SkillCategory), nullable=False, default=SkillCategory.TECHNICAL)
    description = Column(Text, nullable=True)

    graduate_links = relationship("GraduateSkill", back_populates="skill", cascade="all, delete-orphan")
    job_links = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")


class GraduateSkill(Base, TimestampMixin):
    """Association table: which skills a graduate has, and at what self-rated / verified level."""

    __tablename__ = "graduate_skills"

    id = Column(Integer, primary_key=True, index=True)
    graduate_id = Column(Integer, ForeignKey("graduates.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(Float, default=0.0, nullable=False)  # 0-100 self-rated or assessed score
    is_verified = Column(String(20), default="self_rated", nullable=False)  # self_rated | assessed | cv_extracted

    graduate = relationship("Graduate", back_populates="skills")
    skill = relationship("Skill", back_populates="graduate_links")


class SkillGap(Base, TimestampMixin):
    """A computed gap between a graduate's skills and a specific job posting's requirements."""

    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    graduate_id = Column(Integer, ForeignKey("graduates.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    match_percentage = Column(Float, nullable=False, default=0.0)
    missing_skill_ids = Column(Text, nullable=True)  # JSON-encoded list of skill ids
    priority_notes = Column(Text, nullable=True)

    graduate = relationship("Graduate", back_populates="skill_gaps")
    job_posting = relationship("JobPosting", back_populates="skill_gaps")
