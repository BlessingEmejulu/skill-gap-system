"""
User: the authentication/identity record shared by every role.
Role-specific profile data lives in Graduate / Employer (see graduate.py, employer.py).
Administrators and Researchers only ever need this base record.
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.common import UserRole, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.GRADUATE)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Password reset support
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(String(255), nullable=True)

    graduate_profile = relationship("Graduate", back_populates="user", uselist=False, cascade="all, delete-orphan")
    employer_profile = relationship("Employer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
