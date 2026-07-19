from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.employer import Employer, JobPosting, JobSkill
from app.models.graduate import Graduate
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.schemas.skill import JobPostingCreate, JobPostingOut
from app.services.skill_gap_service import save_skill_gap
from app.utils.pagination import Pagination, paginate

router = APIRouter(prefix="/api/jobs", tags=["Job Postings"])


@router.get("", response_model=dict)
def list_jobs(pagination: Pagination = Depends(), db: Session = Depends(get_db)):
    query = db.query(JobPosting).filter(JobPosting.is_active == "active").order_by(JobPosting.created_at.desc())
    result = paginate(query, pagination)
    result["items"] = [JobPostingOut.model_validate(j) for j in result["items"]]
    return result


@router.post("", response_model=JobPostingOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobPostingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.EMPLOYER)),
):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer profile not found.")

    job = JobPosting(
        employer_id=employer.id,
        title=payload.title,
        industry=payload.industry,
        description=payload.description,
        min_experience_years=payload.min_experience_years,
        location=payload.location,
    )
    db.add(job)
    db.flush()  # get job.id before adding child rows

    for req in payload.required_skills:
        db.add(
            JobSkill(
                job_posting_id=job.id,
                skill_id=req.skill_id,
                importance=req.importance,
                is_required=req.is_required,
            )
        )

    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobPostingOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    return job


@router.get("/{job_id}/match")
def get_my_match_for_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.GRADUATE)),
):
    """Computes (and stores) how well the current graduate matches this job."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    graduate = db.query(Graduate).filter(Graduate.user_id == current_user.id).first()
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found.")

    gap = save_skill_gap(db, graduate, job)
    return {
        "job_id": job.id,
        "match_percentage": gap.match_percentage,
        "missing_skill_ids": gap.missing_skill_ids,
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def close_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.EMPLOYER, UserRole.ADMIN)),
):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    job.is_active = "closed"
    db.commit()
