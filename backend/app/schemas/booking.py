
from datetime import date, datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_BOOKING_PEOPLE,
    MAX_FULL_NAME_LENGTH,
    MAX_PHONE_LENGTH,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_phone,
    validate_phone_format,
)


# Dữ liệu của một hành khách
class PassengerCreate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    date_of_birth: date | None = None

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa họ tên hành khách
    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value):
        return normalize_single_line(value)

    # Chuẩn hóa số điện thoại
    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone_input(cls, value):
        return normalize_phone(value)

    # Kiểm tra định dạng số điện thoại
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        return validate_phone_format(value)

    # Kiểm tra ngày sinh không nằm trong tương lai
    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value is not None and value > date.today():
            raise ValueError(
                "Ngày sinh không được lớn hơn ngày hiện tại"
            )

        return value


# Dữ liệu khách hàng gửi khi đặt Tour
class BookingCreate(BaseModel):

    schedule_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    number_of_people: int = Field(
        strict=True,
        ge=1,
        le=MAX_BOOKING_PEOPLE
    )

    passengers: list[PassengerCreate] = Field(
        min_length=1,
        max_length=MAX_BOOKING_PEOPLE
    )

    model_config = ConfigDict(extra="forbid")

    # Kiểm tra số lượng hành khách
    @model_validator(mode="after")
    def validate_passenger_count(self):
        if len(self.passengers) != self.number_of_people:
            raise ValueError(
                "Số lượng hành khách không khớp "
                "với danh sách hành khách"
            )

        return self


# Thông tin hành khách trả về
class PassengerResponse(BaseModel):

    id: int

    full_name: str = Field(
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    date_of_birth: date | None = None

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


# Thông tin tổng quan đơn đặt Tour
class BookingListResponse(BaseModel):

    id: int
    user_id: int
    schedule_id: int
    number_of_people: int
    unit_price: Decimal
    total_amount: Decimal
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Thông tin chi tiết đơn đặt Tour
class BookingResponse(BookingListResponse):

    passengers: list[PassengerResponse]
