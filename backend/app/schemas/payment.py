
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_TRANSACTION_CODE_LENGTH,
)


# Phương thức thanh toán
PaymentMethod = Literal[
    "cash",
    "bank_transfer",
    "online",
]


# Dữ liệu tạo yêu cầu thanh toán
class PaymentCreate(BaseModel):

    booking_id: int = Field(
        strict=True,
        ge=1,
        le=MAX_UNSIGNED_BIGINT
    )

    payment_method: PaymentMethod

    model_config = ConfigDict(
        extra="forbid"
    )


# Dữ liệu thanh toán trả về
class PaymentResponse(BaseModel):

    id: int
    booking_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: str

    transaction_code: str | None = None

    paid_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# Dữ liệu ADMIN xác nhận thanh toán
class PaymentConfirm(BaseModel):

    transaction_code: str | None = Field(
        default=None,
        max_length=MAX_TRANSACTION_CODE_LENGTH
    )

    model_config = ConfigDict(
        extra="forbid"
    )
