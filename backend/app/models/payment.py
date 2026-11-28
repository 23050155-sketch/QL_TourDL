
from sqlalchemy.dialects.mysql import BIGINT

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    booking_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False,
    )

    payment_method = Column(
        Enum("cash", "bank_transfer", "online"),
        nullable=False,
    )

    status = Column(
        Enum("pending", "success", "failed", "refunded"),
        nullable=False,
        default="pending",
    )

    transaction_code = Column(
        String(150),
        unique=True,
        nullable=True,
    )

    paid_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=True,
    )
