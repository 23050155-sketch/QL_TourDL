
from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator,
)

from app.core.validation import (
    MAX_FULL_NAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_PHONE_LENGTH,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_email,
    normalize_phone,
    validate_phone_format,
)


# Schema đăng ký tài khoản
class RegisterRequest(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa họ tên
    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value):
        return normalize_single_line(value)

    # Chuẩn hóa email trước khi kiểm tra
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_input(cls, value):
        return normalize_email(value)

    # Kiểm tra giới hạn email
    @field_validator("email")
    @classmethod
    def validate_email_length(cls, value):
        if len(value) > MAX_EMAIL_LENGTH:
            raise ValueError(
                f"Email không được vượt quá "
                f"{MAX_EMAIL_LENGTH} ký tự"
            )

        return value

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


# Schema đăng nhập
class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa email đăng nhập
    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_input(cls, value):
        return normalize_email(value)

    # Kiểm tra giới hạn email
    @field_validator("email")
    @classmethod
    def validate_email_length(cls, value):
        if len(value) > MAX_EMAIL_LENGTH:
            raise ValueError(
                f"Email không được vượt quá "
                f"{MAX_EMAIL_LENGTH} ký tự"
            )

        return value


# Schema dữ liệu tài khoản trả về
class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: str
    status: str
    created_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


# Schema dữ liệu JWT trả về
class TokenResponse(BaseModel):

    access_token: str
    token_type: str = "bearer"
