from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.academic import University
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/universities", tags=["Universities"])


class UniversityCreate(BaseModel):
    name: str
    state: str | None = None
    ownership: str | None = None


class UniversityOut(UniversityCreate):
    id: int

    class Config:
        from_attributes = True


@router.get("", response_model=list[UniversityOut])
def list_universities(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(University).order_by(University.name).all()


@router.post("", response_model=UniversityOut, status_code=status.HTTP_201_CREATED)
def create_university(
    payload: UniversityCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    if db.query(University).filter(University.name.ilike(payload.name)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="University already exists.")
    university = University(**payload.model_dump())
    db.add(university)
    db.commit()
    db.refresh(university)
    return university
