
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)

from app.schemas.auth import UserResponse

from app.core.validation import (
    MAX_FULL_NAME_LENGTH,
    MAX_PHONE_LENGTH,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_phone,
    validate_phone_format,
)


# Schema cập nhật thông tin cá nhân
class ProfileUpdate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=MAX_FULL_NAME_LENGTH
    )

    phone: str | None = Field(
        default=None,
        max_length=MAX_PHONE_LENGTH
    )

    model_config = ConfigDict(
        extra="forbid"
    )

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


# Schema đổi mật khẩu
class ChangePasswordRequest(BaseModel):

    current_password: str = Field(
        min_length=1,
        max_length=128
    )

    new_password: str = Field(
        min_length=8,
        max_length=128
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=128
    )

    model_config = ConfigDict(
        extra="forbid"
    )


# Schema cập nhật trạng thái tài khoản
class UserStatusUpdate(BaseModel):

    status: Literal["active", "inactive"]

    model_config = ConfigDict(
        extra="forbid"
    )


# Schema danh sách khách hàng có phân trang
class UserListResponse(BaseModel):

    total: int
    page: int
    page_size: int
    total_pages: int

    items: list[UserResponse]
