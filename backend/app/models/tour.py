
from sqlalchemy.dialects.mysql import BIGINT

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    DECIMAL,
    Enum,
    TIMESTAMP,
    text
)

from app.database import Base


class Tour(Base):
    __tablename__ = "tours"

    id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    title = Column(String(255), nullable=False)

    description = Column(Text)

    duration_days = Column(Integer, nullable=False)

    duration_nights = Column(Integer, nullable=False)

    base_price = Column(DECIMAL(12, 2), nullable=False)

    image_url = Column(String(500))

    status = Column(
        Enum("active", "inactive"),
        nullable=False,
        default="active"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
