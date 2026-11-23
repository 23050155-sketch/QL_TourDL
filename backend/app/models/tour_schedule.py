
from sqlalchemy import BigInteger, Column, Date, Enum, ForeignKey, Integer
from app.database import Base


# Ánh xạ bảng lịch khởi hành trong MySQL
class TourSchedule(Base):
    __tablename__ = "tour_schedules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tour_id = Column(
        BigInteger,
        ForeignKey("tours.id"),
        nullable=False
    )
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(
        Enum("open", "closed", "cancelled"),
        nullable=False,
        default="open"
    )
