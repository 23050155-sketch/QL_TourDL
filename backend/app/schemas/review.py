
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Dữ liệu tạo đánh giá
class ReviewCreate(BaseModel):
    tour_id: int = Field(gt=0)

    rating: int = Field(ge=1, le=5)

    comment: str | None = Field(
        default=None,
        max_length=2000
    )


# Dữ liệu cập nhật đánh giá
class ReviewUpdate(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5
    )

    comment: str | None = Field(
        default=None,
        max_length=2000
    )


# Dữ liệu đánh giá trả về
class ReviewResponse(BaseModel):
    id: int
    user_id: int
    tour_id: int
    rating: int
    comment: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


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
