from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.common import UserRole
from app.auth.dependencies import require_roles
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    return {
        "top_demanded_skills": analytics_service.top_demanded_skills(db),
        "most_common_gaps": analytics_service.most_common_gaps(db),
        "graduate_distribution_by_university": analytics_service.graduate_distribution_by_university(db),
    }


@router.get("/top-skills")
def top_skills(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    return analytics_service.top_demanded_skills(db)


@router.get("/skill-gaps")
def skill_gaps(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    return analytics_service.most_common_gaps(db)
