
from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_SCHEDULE_CAPACITY,
    MAX_TOUR_DURATION_DAYS,
)


# Dữ liệu đầu vào dùng chung của lịch khởi hành
class TourScheduleBase(BaseModel):
    tour_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    departure_date: date

    return_date: date

    capacity: int = Field(
        strict=True,
        ge=1,
        le=MAX_SCHEDULE_CAPACITY
    )

    model_config = ConfigDict(extra="forbid")

    # Kiểm tra khoảng thời gian khởi hành
    @model_validator(mode="after")
    def validate_dates(self):
        if self.return_date < self.departure_date:
            raise ValueError(
                "Ngày kết thúc phải lớn hơn hoặc bằng "
                "ngày khởi hành"
            )

        duration_days = (
            self.return_date - self.departure_date
        ).days + 1

        if duration_days > MAX_TOUR_DURATION_DAYS:
            raise ValueError(
                f"Thời lượng lịch khởi hành không được "
                f"vượt quá {MAX_TOUR_DURATION_DAYS} ngày"
            )

        return self


# Dữ liệu ADMIN gửi khi thêm lịch
class TourScheduleCreate(TourScheduleBase):
    pass


# Dữ liệu ADMIN gửi khi cập nhật lịch
class TourScheduleUpdate(TourScheduleBase):
    status: Literal["open", "closed", "cancelled"]


# Dữ liệu trả về cho Frontend
class TourScheduleResponse(BaseModel):
    id: int
    tour_id: int

    departure_date: date
    return_date: date

    capacity: int
    status: str

    booked_slots: int = Field(ge=0)
    remaining_slots: int = Field(ge=0)

    is_full: bool
    is_bookable: bool

    model_config = ConfigDict(
        from_attributes=True
    )
