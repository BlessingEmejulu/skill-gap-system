from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.employer import Employer
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/employers", tags=["Employers"])


class EmployerProfileUpdate(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    company_size: str | None = None
    website: str | None = None
    description: str | None = None


def _get_own_or_403(db: Session, current_user: User) -> Employer:
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employer profile only.")
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer profile not found.")
    return employer


@router.get("/me")
def get_my_company(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_own_or_403(db, current_user)


@router.put("/me")
def update_my_company(
    payload: EmployerProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employer = _get_own_or_403(db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employer, field, value)
    db.commit()
    db.refresh(employer)
    return employer


@router.get("/{employer_id}")
def get_employer(
    employer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found.")
    return employer
