from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.academic import Course
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/courses", tags=["Courses"])


class CourseCreate(BaseModel):
    name: str
    university_id: int | None = None
    faculty: str | None = None
    duration_years: float | None = None


class CourseOut(CourseCreate):
    id: int

    class Config:
        from_attributes = True


@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Course).order_by(Course.name).all()


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    db.delete(course)
    db.commit()
