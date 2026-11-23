
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)

from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    name = Column(
        String(150),
        nullable=False,
    )

    province = Column(
        String(150),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    image_url = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=True,
    )


class TourDestination(Base):
    __tablename__ = "tour_destinations"

    tour_id = Column(
        BigInteger,
        ForeignKey("tours.id"),
        primary_key=True,
    )

    destination_id = Column(
        BigInteger,
        ForeignKey("destinations.id"),
        primary_key=True,
    )

    visit_order = Column(
        Integer,
        nullable=False,
        default=1,
    )
