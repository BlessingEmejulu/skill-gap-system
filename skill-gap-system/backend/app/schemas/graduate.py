import json
from typing import Optional, Any
from pydantic import BaseModel, Field, model_validator


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


class GraduateSkillOut(BaseModel):
    skill_id: int
    proficiency: float

    class Config:
        from_attributes = True


class GraduateOut(BaseModel):
    id: int
    user_id: int
    degree: Optional[str] = None
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None
    state_of_residence: Optional[str] = None
    projects: Optional[list[str]] = None
    internships: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    bio: Optional[str] = None
    cv_file_path: Optional[str] = None
    skills: list[GraduateSkillOut] = []
    skills_count: int = 0

    @model_validator(mode='before')
    @classmethod
    def parse_json_lists(cls, data: Any) -> Any:
        # If data is a SQLAlchemy model, we can access its attributes.
        # But in mode='before', data could be a dict or a model instance.
        if hasattr(data, "__dict__"):
            data_dict = data.__dict__.copy()
        else:
            data_dict = dict(data)
            
        for field in ("projects", "internships", "certifications", "languages"):
            val = data_dict.get(field)
            if isinstance(val, str):
                try:
                    data_dict[field] = json.loads(val)
                except json.JSONDecodeError:
                    data_dict[field] = []
                    
        # Compute skills count if skills relation is loaded
        if hasattr(data, "skills"):
            data_dict["skills_count"] = len(data.skills)
            data_dict["skills"] = [{"skill_id": s.skill_id, "proficiency": s.proficiency} for s in data.skills]
            
        return data_dict

    class Config:
        from_attributes = True
