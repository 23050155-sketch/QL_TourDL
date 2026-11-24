
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Kiểm tra dữ liệu chung của lịch khởi hành
class TourScheduleBase(BaseModel):
    tour_id: int = Field(gt=0)
    departure_date: date
    return_date: date
    capacity: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.return_date < self.departure_date:
            raise ValueError(
                "Ngày kết thúc phải lớn hơn hoặc bằng ngày khởi hành"
            )
        return self


# Dữ liệu ADMIN gửi khi thêm lịch
class TourScheduleCreate(TourScheduleBase):
    pass


# Dữ liệu ADMIN gửi khi cập nhật lịch
class TourScheduleUpdate(TourScheduleBase):
    status: Literal["open", "closed", "cancelled"]



# Dữ liệu trả về cho Frontend
class TourScheduleResponse(TourScheduleBase):
    id: int
    status: str

    booked_slots: int = Field(ge=0)
    remaining_slots: int = Field(ge=0)
    is_full: bool
    is_bookable: bool

    model_config = ConfigDict(
        from_attributes=True
    )

