"""
Prediction: output of the scikit-learn employability model for a graduate.
Recommendation: an AI (Gemma)-generated suggestion tied to a graduate.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin, RiskLevel


class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    graduate_id = Column(Integer, ForeignKey("graduates.id"), nullable=False)

    employability_score = Column(Float, nullable=False)  # 0-100
    employment_probability = Column(Float, nullable=False)  # 0-1
    risk_level = Column(Enum(RiskLevel), nullable=False, default=RiskLevel.MEDIUM)
    skill_gap_percentage = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)

    graduate = relationship("Graduate", back_populates="predictions")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    graduate_id = Column(Integer, ForeignKey("graduates.id"), nullable=False)

    category = Column(String(50), nullable=False)  # missing_skill | certification | course | career_advice | interview_prep
    title = Column(String(255), nullable=False)
    detail = Column(Text, nullable=True)
    source = Column(String(50), default="gemma")  # gemma | system

    graduate = relationship("Graduate", back_populates="recommendations")
