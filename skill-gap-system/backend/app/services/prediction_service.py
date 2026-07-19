"""
Builds GraduateFeatures from stored profile data and runs them through the
employability model, then persists the result as a Prediction row.
"""
import json

from sqlalchemy.orm import Session

from app.models.graduate import Graduate
from app.models.prediction import Prediction
from app.ml.employability_model import employability_model, GraduateFeatures


def _safe_len(json_text: str | None) -> int:
    if not json_text:
        return 0
    try:
        parsed = json.loads(json_text)
        return len(parsed) if isinstance(parsed, list) else 0
    except json.JSONDecodeError:
        return 0


def build_features(graduate: Graduate) -> GraduateFeatures:
    skills = graduate.skills or []
    skill_count = len(skills)
    avg_proficiency = (
        sum(s.proficiency for s in skills) / skill_count if skill_count else 0.0
    )

    return GraduateFeatures(
        cgpa=graduate.cgpa or 0.0,
        skill_count=skill_count,
        avg_skill_proficiency=avg_proficiency,
        project_count=_safe_len(graduate.projects),
        internship_count=_safe_len(graduate.internships),
        certification_count=_safe_len(graduate.certifications),
        experience_years=_safe_len(graduate.internships) * 0.5,  # rough proxy until a dedicated field exists
        avg_soft_skill_score=avg_proficiency,  # refine once soft-skill assessment is scored separately
    )


def run_prediction(db: Session, graduate: Graduate) -> Prediction:
    features = build_features(graduate)
    result = employability_model.predict(features)

    prediction = Prediction(
        graduate_id=graduate.id,
        employability_score=result["employability_score"],
        employment_probability=result["employment_probability"],
        risk_level=result["risk_level"],
        confidence=result.get("confidence"),
        model_version=result.get("model_version"),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
