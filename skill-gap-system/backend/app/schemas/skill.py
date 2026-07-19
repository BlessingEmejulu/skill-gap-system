from typing import Optional
from pydantic import BaseModel, Field

from app.models.common import SkillCategory


class SkillCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    category: SkillCategory = SkillCategory.TECHNICAL
    description: Optional[str] = None


class SkillOut(BaseModel):
    id: int
    name: str
    category: SkillCategory
    description: Optional[str] = None

    class Config:
        from_attributes = True


class JobSkillIn(BaseModel):
    skill_id: int
    importance: float = Field(default=1.0, ge=0, le=5)
    is_required: str = "required"


class JobPostingCreate(BaseModel):
    title: str
    industry: Optional[str] = None
    description: Optional[str] = None
    min_experience_years: float = 0.0
    location: Optional[str] = None
    required_skills: list[JobSkillIn] = []


class JobPostingOut(BaseModel):
    id: int
    employer_id: int
    title: str
    industry: Optional[str] = None
    location: Optional[str] = None
    is_active: str

    class Config:
        from_attributes = True
