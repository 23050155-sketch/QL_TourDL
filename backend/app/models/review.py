
from sqlalchemy import (
    BigInteger,
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
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )

    tour_id = Column(
        BigInteger,
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
