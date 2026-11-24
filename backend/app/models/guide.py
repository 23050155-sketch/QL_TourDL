
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Enum,
    func,
)

from app.database import Base


class TourGuide(Base):
    __tablename__ = "tour_guides"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    full_name = Column(String(150), nullable=False)

    phone = Column(String(20), nullable=True)

    email = Column(
        String(190),
        unique=True,
        nullable=True
    )

    experience_years = Column(
        Integer,
        nullable=True,
        server_default="0"
    )

    status = Column(
        Enum("active", "inactive"),
        nullable=False,
        server_default="active"
    )

    created_at = Column(
        DateTime,
        nullable=True,
        server_default=func.now()
    )


class GuideAssignment(Base):
    __tablename__ = "guide_assignments"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    schedule_id = Column(
        BigInteger,
        ForeignKey("tour_schedules.id"),
        nullable=False
    )

    guide_id = Column(
        BigInteger,
        ForeignKey("tour_guides.id"),
        nullable=False
    )

    assigned_at = Column(
        DateTime,
        nullable=True,
        server_default=func.now()
    )
