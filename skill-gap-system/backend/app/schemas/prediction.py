from typing import Optional
from pydantic import BaseModel

from app.models.common import RiskLevel


class PredictionRequest(BaseModel):
    """Optional overrides; if omitted, the service pulls the graduate's stored profile."""
    graduate_id: int


class PredictionOut(BaseModel):
    id: int
    graduate_id: int
    employability_score: float
    employment_probability: float
    risk_level: RiskLevel
    skill_gap_percentage: Optional[float] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    id: int
    category: str
    title: str
    detail: Optional[str] = None

    class Config:
        from_attributes = True
