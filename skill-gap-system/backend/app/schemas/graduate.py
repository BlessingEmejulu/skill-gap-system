from typing import Optional
from pydantic import BaseModel, Field


class GraduateProfileUpdate(BaseModel):
    university_id: Optional[int] = None
    course_id: Optional[int] = None
    degree: Optional[str] = None
    cgpa: Optional[float] = Field(default=None, ge=0, le=5)
    graduation_year: Optional[int] = None
    phone: Optional[str] = None
    state_of_residence: Optional[str] = None
    bio: Optional[str] = None
    projects: Optional[list[str]] = None
    internships: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    languages: Optional[list[str]] = None


class GraduateSkillIn(BaseModel):
    skill_id: int
    proficiency: float = Field(ge=0, le=100)


class GraduateOut(BaseModel):
    id: int
    user_id: int
    degree: Optional[str] = None
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None
    state_of_residence: Optional[str] = None

    class Config:
        from_attributes = True
