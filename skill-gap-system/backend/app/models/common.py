"""
Shared enums and mixins used across multiple model files.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr


class UserRole(str, enum.Enum):
    ADMIN = "administrator"
    GRADUATE = "graduate"
    EMPLOYER = "employer"
    RESEARCHER = "researcher"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillCategory(str, enum.Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    DIGITAL_LITERACY = "digital_literacy"
    INDUSTRY_READINESS = "industry_readiness"


class TimestampMixin:
    """Adds created_at / updated_at columns to any model that inherits it."""

    @declared_attr
    def created_at(cls):  # noqa: N805
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):  # noqa: N805
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
