
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Dữ liệu đầu vào khi ADMIN tạo tour mới
class TourCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    duration_days: int = Field(gt=0)
    duration_nights: int = Field(ge=0)
    base_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    image_url: str | None = None


# Dữ liệu đầu vào khi ADMIN cập nhật tour
class TourUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    duration_days: int = Field(gt=0)
    duration_nights: int = Field(ge=0)
    base_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    image_url: str | None = None
    status: Literal["active", "inactive"]


# Dữ liệu tour trả về cho Frontend
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
