from typing import Literal
from app.schemas.auth import UserResponse

from pydantic import BaseModel, Field, ConfigDict


class ProfileUpdate(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=20
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )





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
