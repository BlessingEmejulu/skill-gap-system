import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.common import UserRole
from app.auth.dependencies import get_current_user, require_roles
from app.services import analytics_service
from app.utils.report_generator import generate_pdf_report, generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

REPORTS_DIR = "./reports"


@router.post("/analytics")
def generate_analytics_report(
    file_format: str = "pdf",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.RESEARCHER)),
):
    if file_format not in ("pdf", "xlsx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file_format must be 'pdf' or 'xlsx'.")

    rows = analytics_service.top_demanded_skills(db)
    filepath = (
        generate_pdf_report("Top Demanded Skills", rows, REPORTS_DIR)
        if file_format == "pdf"
        else generate_excel_report("Top Demanded Skills", rows, REPORTS_DIR)
    )

    report = Report(
        requested_by_user_id=current_user.id,
        report_type="analytics",
        file_format=file_format,
        file_path=filepath,
        status="ready",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"report_id": report.id, "download_url": f"/api/reports/{report.id}/download"}


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    if current_user.role != UserRole.ADMIN and current_user.id != report.requested_by_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to download this report.")

    media_type = "application/pdf" if report.file_format == "pdf" else (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    return FileResponse(report.file_path, media_type=media_type, filename=os.path.basename(report.file_path))


@router.get("/me")
def my_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Report)
        .filter(Report.requested_by_user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
