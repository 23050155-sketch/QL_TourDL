
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_FULL_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_GUIDE_EXPERIENCE_YEARS,
)


# Dữ liệu tạo hướng dẫn viên
class GuideCreate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    email: str | None = Field(
        default=None,
        max_length=MAX_EMAIL_LENGTH
    )

    experience_years: int | None = Field(
        default=0,
        strict=True,
        ge=0,
        le=MAX_GUIDE_EXPERIENCE_YEARS
    )

    model_config = ConfigDict(extra="forbid")


# Dữ liệu cập nhật hướng dẫn viên
class GuideUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    email: str | None = Field(
        default=None,
        max_length=MAX_EMAIL_LENGTH
    )

    experience_years: int | None = Field(
        default=None,
        strict=True,
        ge=0,
        le=MAX_GUIDE_EXPERIENCE_YEARS
    )

    status: Literal["active", "inactive"] | None = None

    model_config = ConfigDict(extra="forbid")

    # Không cho phép cập nhật trường bắt buộc thành null
    @model_validator(mode="after")
    def validate_required_fields(self):
        required_fields = ("full_name", "status")

        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"{field_name} không được là null"
                )

        return self


# Thông tin hướng dẫn viên công khai
class GuidePublicResponse(BaseModel):
    id: int
    full_name: str
    experience_years: int | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Thông tin liên hệ HDV dành cho khách đã thanh toán
class GuideContactResponse(GuidePublicResponse):
    phone: str | None = None
    email: str | None = None


# Thông tin hướng dẫn viên dành cho ADMIN
class GuideResponse(BaseModel):
    id: int
    full_name: str
    phone: str | None = None
    email: str | None = None
    experience_years: int | None = None
    status: str
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Dữ liệu phân công hướng dẫn viên
class GuideAssignmentCreate(BaseModel):
    schedule_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    guide_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    model_config = ConfigDict(extra="forbid")


# Thông tin phân công hướng dẫn viên
class GuideAssignmentResponse(BaseModel):
    id: int
    schedule_id: int
    guide_id: int
    assigned_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )
