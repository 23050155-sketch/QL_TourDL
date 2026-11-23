
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PaymentMethod = Literal[
    "cash",
    "bank_transfer",
    "online",
]


class PaymentCreate(BaseModel):
    booking_id: int = Field(gt=0)
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: str
    transaction_code: str | None = None
    paid_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentConfirm(BaseModel):
    transaction_code: str | None = Field(
        default=None,
        max_length=150,
    )
