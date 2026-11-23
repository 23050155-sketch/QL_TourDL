
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# Dữ liệu của một hành khách
class PassengerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    date_of_birth: date | None = None
    phone: str | None = Field(default=None, max_length=20)


# Dữ liệu khách hàng gửi khi đặt Tour
class BookingCreate(BaseModel):
    schedule_id: int = Field(gt=0)
    number_of_people: int = Field(gt=0)
    passengers: list[PassengerCreate] = Field(min_length=1)


# Thông tin hành khách trả về
class PassengerResponse(PassengerCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Thông tin đơn đặt Tour trả về
class BookingResponse(BaseModel):
    id: int
    user_id: int
    schedule_id: int
    number_of_people: int
    unit_price: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime | None = None
    passengers: list[PassengerResponse]

    model_config = ConfigDict(from_attributes=True)
