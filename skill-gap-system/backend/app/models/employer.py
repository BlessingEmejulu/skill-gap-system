"""
Employer: the role-specific profile for a User with role == EMPLOYER.
JobPosting: a job listed by an employer, with required skills via JobSkill.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin


class Employer(Base, TimestampMixin):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    company_name = Column(String(255), nullable=False)
    industry = Column(String(150), nullable=True)
    company_size = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="employer_profile")
    job_postings = relationship("JobPosting", back_populates="employer", cascade="all, delete-orphan")


class JobPosting(Base, TimestampMixin):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("employers.id"), nullable=False)

    title = Column(String(255), nullable=False)
    industry = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    min_experience_years = Column(Float, default=0.0)
    location = Column(String(150), nullable=True)
    is_active = Column(String(10), default="active")  # active | closed

    employer = relationship("Employer", back_populates="job_postings")
    required_skills = relationship("JobSkill", back_populates="job_posting", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="job_posting", cascade="all, delete-orphan")


class JobSkill(Base, TimestampMixin):
    """Association table: which skills a job posting requires, and how important each is."""

    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    importance = Column(Float, default=1.0, nullable=False)  # weight used in match-percentage calc
    is_required = Column(String(10), default="required")  # required | preferred

    job_posting = relationship("JobPosting", back_populates="required_skills")
    skill = relationship("Skill", back_populates="job_links")
