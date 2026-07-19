import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.models.skill import Skill
from app.models.prediction import Recommendation
from app.models.common import UserRole
from app.auth.dependencies import require_roles
from app.schemas.prediction import RecommendationOut
from app.ai.gemma_client import gemma_client

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/me/generate", response_model=list[RecommendationOut])
async def generate_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.GRADUATE)),
):
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")

    graduate_skill_ids = {gs.skill_id for gs in graduate.skills}
    all_skills = db.query(Skill).all()
    # Placeholder "missing" set until this graduate has matched against real job postings.
    missing_skill_names = [s.name for s in all_skills if s.id not in graduate_skill_ids][:10]

    profile_summary = {
        "degree": graduate.degree,
        "cgpa": graduate.cgpa,
        "skill_count": len(graduate.skills),
    }

    generated = await gemma_client.generate_recommendations(profile_summary, missing_skill_names)

    saved: list[Recommendation] = []
    for item in generated:
        rec = Recommendation(
            graduate_id=graduate.id,
            category=item.get("category", "career_advice"),
            title=item.get("title", "Recommendation"),
            detail=item.get("detail"),
        )
        db.add(rec)
        saved.append(rec)
    db.commit()
    for rec in saved:
        db.refresh(rec)

    return saved


@router.get("/me", response_model=list[RecommendationOut])
def my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.GRADUATE)),
):
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")
    return (
        db.query(Recommendation)
        .filter(Recommendation.graduate_id == graduate.id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )
