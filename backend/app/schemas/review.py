
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
    MIN_REVIEW_RATING,
    MAX_REVIEW_RATING,
    MAX_REVIEW_COMMENT_LENGTH,
)

from app.core.normalization import (
    normalize_optional_multiline,
)


# Dữ liệu tạo đánh giá
class ReviewCreate(BaseModel):

    tour_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    rating: int = Field(
        strict=True,
        ge=MIN_REVIEW_RATING,
        le=MAX_REVIEW_RATING
    )

    comment: str | None = Field(
        default=None,
        max_length=MAX_REVIEW_COMMENT_LENGTH
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # Chuẩn hóa nội dung bình luận
    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, value):
        return normalize_optional_multiline(value)


# Dữ liệu cập nhật đánh giá
class ReviewUpdate(BaseModel):

    rating: int | None = Field(
        default=None,
        strict=True,
        ge=MIN_REVIEW_RATING,
        le=MAX_REVIEW_RATING
    )

    comment: str | None = Field(
        default=None,
        max_length=MAX_REVIEW_COMMENT_LENGTH
    )

    model_config = ConfigDict(
        extra="forbid"
    )

    # Chuẩn hóa nội dung bình luận
    @field_validator("comment", mode="before")
    @classmethod
    def normalize_comment(cls, value):
        return normalize_optional_multiline(value)

    # Không cho phép cập nhật rating thành null
    @model_validator(mode="after")
    def validate_rating(self):

        if (
            "rating" in self.model_fields_set
            and self.rating is None
        ):
            raise ValueError(
                "Điểm đánh giá không được là null"
            )

        return self


# Dữ liệu đánh giá công khai
class ReviewPublicResponse(BaseModel):

    id: int
    tour_id: int
    rating: int
    comment: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Dữ liệu đánh giá trả về
class ReviewResponse(BaseModel):

    id: int
    user_id: int
    tour_id: int
    rating: int
    comment: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Dữ liệu thống kê đánh giá
class ReviewSummary(BaseModel):

    tour_id: int
    average_rating: float
    total_reviews: int

    five_stars: int
    four_stars: int
    three_stars: int
    two_stars: int
    one_star: int
