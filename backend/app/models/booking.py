
from sqlalchemy.dialects.mysql import BIGINT

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    func,
)

from sqlalchemy.orm import relationship
from app.database import Base


# Ánh xạ bảng bookings trong MySQL
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    schedule_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("tour_schedules.id"),
        nullable=False,
    )

    number_of_people = Column(Integer, nullable=False)

    unit_price = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(
        Enum(
            "pending",
            "awaiting_payment",
            "paid",
            "completed",
            "rejected",
            "cancelled",
        ),
        nullable=False,
        default="pending",
    )

    created_at = Column(DateTime, server_default=func.now())

    passengers = relationship(
        "BookingPassenger",
        back_populates="booking",
        cascade="all, delete-orphan",
    )


# Ánh xạ bảng booking_passengers trong MySQL
class BookingPassenger(Base):
    __tablename__ = "booking_passengers"

    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)

    booking_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("bookings.id"),
        nullable=False,
    )

    full_name = Column(
        "full_name",
        __import__("sqlalchemy").String(150),
        nullable=False,
    )

    date_of_birth = Column(
        __import__("sqlalchemy").Date,
        nullable=True,
    )

    phone = Column(
        __import__("sqlalchemy").String(20),
        nullable=True,
    )

    booking = relationship(
        "Booking",
        back_populates="passengers",
    )
