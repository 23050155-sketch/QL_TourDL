
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.validation import (
    MAX_TOUR_TITLE_LENGTH,
    MAX_TOUR_DURATION_DAYS,
    MAX_TOUR_DURATION_NIGHTS,
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGE_URL_LENGTH,
)


# Dữ liệu đầu vào dùng chung của Tour
class TourBase(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=MAX_TOUR_TITLE_LENGTH
    )

    description: str | None = Field(
        default=None,
        max_length=MAX_DESCRIPTION_LENGTH
    )

    duration_days: int = Field(
        strict=True,
        ge=1,
        le=MAX_TOUR_DURATION_DAYS
    )

    duration_nights: int = Field(
        strict=True,
        ge=0,
        le=MAX_TOUR_DURATION_NIGHTS
    )

    base_price: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )

    image_url: str | None = Field(
        default=None,
        max_length=MAX_IMAGE_URL_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    # Kiểm tra tương quan giữa số ngày và số đêm
    @model_validator(mode="after")
    def validate_duration(self):
        if self.duration_nights >= self.duration_days:
            raise ValueError(
                "Số đêm phải nhỏ hơn số ngày của Tour"
            )

        return self


# Dữ liệu đầu vào khi ADMIN tạo Tour mới
class TourCreate(TourBase):
    pass


# Dữ liệu đầu vào khi ADMIN cập nhật Tour
class TourUpdate(TourBase):
    status: Literal["active", "inactive"]


# Dữ liệu Tour trả về cho Frontend
class TourResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    duration_days: int
    duration_nights: int
    base_price: Decimal
    image_url: str | None = None
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Thông tin Tour kèm thống kê đánh giá
class TourSearchItem(TourResponse):
    average_rating: float = 0.0
    total_reviews: int = 0


# Kết quả tìm kiếm Tour có phân trang
class TourSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[TourSearchItem]
