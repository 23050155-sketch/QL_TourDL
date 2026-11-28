
from sqlalchemy.dialects.mysql import BIGINT

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tour_id",
            name="uq_reviews_user_tour"
        ),
    )

    id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=False
    )

    tour_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("tours.id"),
        nullable=False
    )

    rating = Column(
        Integer,
        nullable=False
    )

    comment = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=True,
        server_default=func.now()
    )
