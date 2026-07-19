from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.skill import Skill
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.skill import SkillCreate, SkillOut

router = APIRouter(prefix="/api/skills", tags=["Skills"])


@router.get("", response_model=list[SkillOut])
def list_skills(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Skill).order_by(Skill.name).all()


@router.post("", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def create_skill(
    payload: SkillCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    existing = db.query(Skill).filter(Skill.name.ilike(payload.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Skill already exists.")
    skill = Skill(**payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found.")
    db.delete(skill)
    db.commit()
