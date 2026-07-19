from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.graduate import Graduate
from app.models.prediction import Prediction
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.prediction import PredictionOut
from app.services.prediction_service import run_prediction

router = APIRouter(prefix="/api/prediction", tags=["Prediction"])


@router.post("/me", response_model=PredictionOut)
def predict_my_employability(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.GRADUATE)),
):
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")
    return run_prediction(db, graduate)


@router.get("/me/history", response_model=list[PredictionOut])
def my_prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.GRADUATE)),
):
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")
    return (
        db.query(Prediction)
        .filter(Prediction.graduate_id == graduate.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )


@router.post("/{graduate_id}", response_model=PredictionOut)
def predict_for_graduate(
    graduate_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    graduate = db.query(Graduate).filter(Graduate.id == graduate_id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate not found.")
    return run_prediction(db, graduate)
