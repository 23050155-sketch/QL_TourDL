
from sqlalchemy import Column, String, Enum, TIMESTAMP, text
from sqlalchemy.dialects.mysql import BIGINT

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    full_name = Column(String(150), nullable=False)

    email = Column(
        String(190),
        nullable=False,
        unique=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    phone = Column(String(20))

    role = Column(
        Enum("admin", "customer"),
        nullable=False,
        default="customer"
    )

    status = Column(
        Enum("active", "inactive"),
        nullable=False,
        default="active"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
