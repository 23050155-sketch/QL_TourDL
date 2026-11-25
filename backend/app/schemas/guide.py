
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_FULL_NAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_GUIDE_EXPERIENCE_YEARS,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_email,
    normalize_phone,
    validate_phone_format,
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

    email: EmailStr | None = None

    experience_years: int | None = Field(
        default=0,
        strict=True,
        ge=0,
        le=MAX_GUIDE_EXPERIENCE_YEARS
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa họ tên
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

    # Chuẩn hóa email tùy chọn
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_input(cls, value):
        value = normalize_email(value)

        if isinstance(value, str) and value == "":
            return None

        return value

    # Kiểm tra độ dài email
    @field_validator("email")
    @classmethod
    def validate_email_length(cls, value):
        if value is not None and len(value) > MAX_EMAIL_LENGTH:
            raise ValueError(
                f"Email không được vượt quá "
                f"{MAX_EMAIL_LENGTH} ký tự"
            )

        return value


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

    email: EmailStr | None = None

    experience_years: int | None = Field(
        default=None,
        strict=True,
        ge=0,
        le=MAX_GUIDE_EXPERIENCE_YEARS
    )

    status: Literal["active", "inactive"] | None = None

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa họ tên
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

    # Chuẩn hóa email tùy chọn
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_input(cls, value):
        value = normalize_email(value)

        if isinstance(value, str) and value == "":
            return None

        return value

    # Kiểm tra độ dài email
    @field_validator("email")
    @classmethod
    def validate_email_length(cls, value):
        if value is not None and len(value) > MAX_EMAIL_LENGTH:
            raise ValueError(
                f"Email không được vượt quá "
                f"{MAX_EMAIL_LENGTH} ký tự"
            )

        return value

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
