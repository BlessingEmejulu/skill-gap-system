"""
Aggregation queries for the analytics dashboard: top demanded skills,
most common skill gaps, and graduate distribution by university.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.skill import Skill, GraduateSkill, SkillGap
from app.models.employer import JobSkill
from app.models.graduate import Graduate
from app.models.academic import University


def top_demanded_skills(db: Session, limit: int = 10):
    rows = (
        db.query(Skill.name, func.count(JobSkill.id).label("demand"))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .group_by(Skill.name)
        .order_by(func.count(JobSkill.id).desc())
        .limit(limit)
        .all()
    )
    return [{"skill": name, "demand": demand} for name, demand in rows]


def most_common_gaps(db: Session, limit: int = 10):
    """Skills most frequently missing across all computed skill gaps."""
    gaps = db.query(SkillGap.missing_skill_ids).all()
    counts: dict[int, int] = {}
    for (missing_json,) in gaps:
        if not missing_json:
            continue
        import json

        try:
            ids = json.loads(missing_json)
        except json.JSONDecodeError:
            continue
        for skill_id in ids:
            counts[skill_id] = counts.get(skill_id, 0) + 1

    top_ids = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    if not top_ids:
        return []

    id_list = [i for i, _ in top_ids]
    skills = {s.id: s.name for s in db.query(Skill).filter(Skill.id.in_(id_list)).all()}
    return [{"skill": skills.get(i, f"skill_{i}"), "count": c} for i, c in top_ids]


def graduate_distribution_by_university(db: Session, limit: int = 10):
    rows = (
        db.query(University.name, func.count(Graduate.id).label("graduate_count"))
        .join(Graduate, Graduate.university_id == University.id)
        .group_by(University.name)
        .order_by(func.count(Graduate.id).desc())
        .limit(limit)
        .all()
    )
    return [{"university": name, "graduate_count": count} for name, count in rows]
