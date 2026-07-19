"""
Import every model here so that Base.metadata.create_all() picks up all tables
with a single `from app import models` / `import app.models`.
"""
from app.models.user import User
from app.models.academic import University, Course
from app.models.skill import Skill, GraduateSkill, SkillGap
from app.models.graduate import Graduate
from app.models.employer import Employer, JobPosting, JobSkill
from app.models.prediction import Prediction, Recommendation
from app.models.report import Report, Notification

__all__ = [
    "User",
    "University",
    "Course",
    "Skill",
    "GraduateSkill",
    "SkillGap",
    "Graduate",
    "Employer",
    "JobPosting",
    "JobSkill",
    "Prediction",
    "Recommendation",
    "Report",
    "Notification",
]
