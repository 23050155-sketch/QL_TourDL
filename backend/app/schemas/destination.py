
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DestinationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    province: str = Field(min_length=2, max_length=150)
    description: str | None = None
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class DestinationUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    province: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )
    description: str | None = None
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )


class DestinationResponse(DestinationCreate):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TourDestinationCreate(BaseModel):
    destination_id: int = Field(gt=0)
    visit_order: int = Field(default=1, ge=1)


class TourDestinationResponse(BaseModel):
    tour_id: int
    destination_id: int
    visit_order: int

    model_config = ConfigDict(from_attributes=True)
