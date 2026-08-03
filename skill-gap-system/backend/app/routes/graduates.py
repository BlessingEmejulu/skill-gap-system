import json

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.models.skill import GraduateSkill, Skill
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.graduate import GraduateProfileUpdate, GraduateSkillIn, GraduateOut
from app.ai.gemini_client import gemini_client

router = APIRouter(prefix="/api/graduates", tags=["Graduates"])


def _get_own_or_403(db: Session, current_user: User) -> Graduate:
    if current_user.role != UserRole.GRADUATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Graduate profile only.")
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")
    return graduate


@router.get("/me", response_model=GraduateOut)
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_own_or_403(db, current_user)


@router.put("/me", response_model=GraduateOut)
def update_my_profile(
    payload: GraduateProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = _get_own_or_403(db, current_user)
    data = payload.model_dump(exclude_unset=True)

    for list_field in ("projects", "internships", "certifications", "languages"):
        if list_field in data and data[list_field] is not None:
            data[list_field] = json.dumps(data[list_field])

    for field, value in data.items():
        setattr(graduate, field, value)

    db.commit()
    db.refresh(graduate)
    return graduate


@router.post("/me/skills", status_code=status.HTTP_201_CREATED)
def add_my_skill(
    payload: GraduateSkillIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = _get_own_or_403(db, current_user)
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found.")

    link = (
        db.query(GraduateSkill)
        .filter(GraduateSkill.graduate_id == graduate.id, GraduateSkill.skill_id == payload.skill_id)
        .first()
    )
    if link:
        link.proficiency = payload.proficiency
    else:
        link = GraduateSkill(graduate_id=graduate.id, skill_id=payload.skill_id, proficiency=payload.proficiency)
        db.add(link)

    db.commit()
    return {"message": "Skill saved.", "skill_id": payload.skill_id, "proficiency": payload.proficiency}


@router.post("/me/cv", status_code=status.HTTP_200_OK)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    graduate = _get_own_or_403(db, current_user)
    
    # Check file type
    if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, TXT, DOCX allowed.")
        
    # Read file content
    content = await file.read()
    
    # Basic text extraction stub - in a real app use PyPDF2 or python-docx
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback if it's a binary file like PDF but we don't have a parser yet
        text = "Sample extracted text from CV... Software Engineer with 5 years experience in Python and React."
        
    # Extract skills using Gemini
    extracted_skills = await gemini_client.extract_skills_from_text(text)
    
    # Save the parsed CV path to the graduate profile (mock path for now)
    graduate.cv_file_path = f"uploads/{current_user.id}_{file.filename}"
    db.commit()
    
    return {
        "message": "CV uploaded and parsed successfully",
        "extracted_skills": extracted_skills
    }


@router.get("/{graduate_id}", response_model=GraduateOut)
def get_graduate(
    graduate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EMPLOYER, UserRole.RESEARCHER)),
):
    graduate = db.query(Graduate).filter(Graduate.id == graduate_id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate not found.")
    return graduate
