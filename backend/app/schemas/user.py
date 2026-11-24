
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.auth import UserResponse

from app.core.validation import (
    MAX_FULL_NAME_LENGTH,
    MAX_PHONE_LENGTH,
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
        extra="forbid",
        str_strip_whitespace=True
    )


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
