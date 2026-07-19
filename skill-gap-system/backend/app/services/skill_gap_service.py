"""
Compares a graduate's skills against a job posting's required skills and
computes a weighted match percentage plus the list of missing skills.
"""
import json

from sqlalchemy.orm import Session

from app.models.graduate import Graduate
from app.models.employer import JobPosting
from app.models.skill import SkillGap


def compute_match(db: Session, graduate: Graduate, job: JobPosting) -> dict:
    graduate_skill_ids = {gs.skill_id for gs in graduate.skills}

    total_weight = 0.0
    matched_weight = 0.0
    missing_skill_ids: list[int] = []

    for req in job.required_skills:
        weight = req.importance or 1.0
        total_weight += weight
        if req.skill_id in graduate_skill_ids:
            matched_weight += weight
        else:
            missing_skill_ids.append(req.skill_id)

    match_percentage = round((matched_weight / total_weight) * 100, 1) if total_weight else 0.0

    return {
        "match_percentage": match_percentage,
        "missing_skill_ids": missing_skill_ids,
    }


def save_skill_gap(db: Session, graduate: Graduate, job: JobPosting) -> SkillGap:
    result = compute_match(db, graduate, job)

    existing = (
        db.query(SkillGap)
        .filter(SkillGap.graduate_id == graduate.id, SkillGap.job_posting_id == job.id)
        .first()
    )
    if existing:
        existing.match_percentage = result["match_percentage"]
        existing.missing_skill_ids = json.dumps(result["missing_skill_ids"])
        db.commit()
        db.refresh(existing)
        return existing

    gap = SkillGap(
        graduate_id=graduate.id,
        job_posting_id=job.id,
        match_percentage=result["match_percentage"],
        missing_skill_ids=json.dumps(result["missing_skill_ids"]),
    )
    db.add(gap)
    db.commit()
    db.refresh(gap)
    return gap
