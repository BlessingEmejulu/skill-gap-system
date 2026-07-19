"""
Report: a generated PDF/Excel export, kept as a record for re-download.
Notification: an in-app notification for a user.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    requested_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # employability | skill_gap | analytics
    file_format = Column(String(10), nullable=False)  # pdf | xlsx
    file_path = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending | ready | failed


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="notifications")
