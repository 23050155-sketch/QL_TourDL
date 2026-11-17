
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


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
