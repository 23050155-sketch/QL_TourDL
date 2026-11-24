
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GuideCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=190)
    experience_years: int | None = Field(default=0, ge=0)


class GuideUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=190)
    experience_years: int | None = Field(default=None, ge=0)
    status: str | None = Field(
        default=None,
        pattern="^(active|inactive)$"
    )


class GuideResponse(BaseModel):
    id: int
    full_name: str
    phone: str | None = None
    email: str | None = None
    experience_years: int | None = None
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GuideAssignmentCreate(BaseModel):
    schedule_id: int = Field(gt=0)
    guide_id: int = Field(gt=0)


class GuideAssignmentResponse(BaseModel):
    id: int
    schedule_id: int
    guide_id: int
    assigned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
