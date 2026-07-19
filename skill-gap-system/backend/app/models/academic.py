"""
University and Course: reference data for a graduate's academic background.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin


class University(Base, TimestampMixin):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    state = Column(String(100), nullable=True)
    ownership = Column(String(50), nullable=True)  # federal / state / private

    graduates = relationship("Graduate", back_populates="university")
    courses = relationship("Course", back_populates="university", cascade="all, delete-orphan")


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    faculty = Column(String(255), nullable=True)
    duration_years = Column(Float, nullable=True)

    university = relationship("University", back_populates="courses")
    graduates = relationship("Graduate", back_populates="course")
