"""
Graduate: the role-specific profile for a User with role == GRADUATE.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import TimestampMixin


class Graduate(Base, TimestampMixin):
    __tablename__ = "graduates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    degree = Column(String(150), nullable=True)  # e.g. B.Sc, B.Eng, HND
    cgpa = Column(Float, nullable=True)
    graduation_year = Column(Integer, nullable=True)

    phone = Column(String(30), nullable=True)
    state_of_residence = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    cv_file_path = Column(String(500), nullable=True)

    projects = Column(Text, nullable=True)  # JSON-encoded list
    internships = Column(Text, nullable=True)  # JSON-encoded list
    certifications = Column(Text, nullable=True)  # JSON-encoded list
    languages = Column(Text, nullable=True)  # JSON-encoded list

    user = relationship("User", back_populates="graduate_profile")
    university = relationship("University", back_populates="graduates")
    course = relationship("Course", back_populates="graduates")
    skills = relationship("GraduateSkill", back_populates="graduate", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="graduate", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="graduate", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="graduate", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Graduate id={self.id} user_id={self.user_id}>"
