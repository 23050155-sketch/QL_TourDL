
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_SIGNED_INT,
    MAX_DESTINATION_NAME_LENGTH,
    MAX_PROVINCE_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGE_URL_LENGTH,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_optional_multiline,
    normalize_optional_url,
    validate_image_url,
)


# Dữ liệu tạo địa điểm
class DestinationCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=MAX_DESTINATION_NAME_LENGTH
    )

    province: str = Field(
        min_length=2,
        max_length=MAX_PROVINCE_LENGTH
    )

    description: str | None = Field(
        default=None,
        max_length=MAX_DESCRIPTION_LENGTH
    )

    image_url: str | None = Field(
        default=None,
        max_length=MAX_IMAGE_URL_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa tên địa điểm và tỉnh thành
    @field_validator("name", "province", mode="before")
    @classmethod
    def normalize_name_and_province(cls, value):
        return normalize_single_line(value)

    # Chuẩn hóa mô tả
    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        return normalize_optional_multiline(value)

    # Chuẩn hóa URL hình ảnh
    @field_validator("image_url", mode="before")
    @classmethod
    def normalize_image_url_input(cls, value):
        return normalize_optional_url(value)

    # Kiểm tra URL hình ảnh
    @field_validator("image_url")
    @classmethod
    def validate_image_url_input(cls, value):
        return validate_image_url(value)


# Dữ liệu cập nhật địa điểm
class DestinationUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=MAX_DESTINATION_NAME_LENGTH
    )

    province: str | None = Field(
        default=None,
        min_length=2,
        max_length=MAX_PROVINCE_LENGTH
    )

    description: str | None = Field(
        default=None,
        max_length=MAX_DESCRIPTION_LENGTH
    )

    image_url: str | None = Field(
        default=None,
        max_length=MAX_IMAGE_URL_LENGTH
    )

    model_config = ConfigDict(extra="forbid")

    # Chuẩn hóa tên địa điểm và tỉnh thành
    @field_validator("name", "province", mode="before")
    @classmethod
    def normalize_name_and_province(cls, value):
        return normalize_single_line(value)

    # Chuẩn hóa mô tả
    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        return normalize_optional_multiline(value)

    # Chuẩn hóa URL hình ảnh
    @field_validator("image_url", mode="before")
    @classmethod
    def normalize_image_url_input(cls, value):
        return normalize_optional_url(value)

    # Kiểm tra URL hình ảnh
    @field_validator("image_url")
    @classmethod
    def validate_image_url_input(cls, value):
        return validate_image_url(value)

    # Không cho phép cập nhật trường bắt buộc thành null
    @model_validator(mode="after")
    def validate_required_fields(self):
        required_fields = ("name", "province")

        for field_name in required_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"{field_name} không được là null"
                )

        return self


# Thông tin địa điểm trả về
class DestinationResponse(BaseModel):

    id: int

    name: str = Field(
        min_length=2,
        max_length=MAX_DESTINATION_NAME_LENGTH
    )

    province: str = Field(
        min_length=2,
        max_length=MAX_PROVINCE_LENGTH
    )

    description: str | None = None

    image_url: str | None = Field(
        default=None,
        max_length=MAX_IMAGE_URL_LENGTH
    )

    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Dữ liệu thêm địa điểm vào Tour
class TourDestinationCreate(BaseModel):

    destination_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    visit_order: int = Field(
        default=1,
        strict=True,
        ge=1,
        le=MAX_SIGNED_INT
    )

    model_config = ConfigDict(extra="forbid")


# Thông tin địa điểm thuộc Tour
class TourDestinationResponse(BaseModel):

    tour_id: int
    destination_id: int
    visit_order: int

    model_config = ConfigDict(
        from_attributes=True
    )
