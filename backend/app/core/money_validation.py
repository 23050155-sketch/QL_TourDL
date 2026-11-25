
from decimal import Decimal, localcontext

from app.core.validation import (
    MAX_TOUR_PRICE,
    MAX_BOOKING_PEOPLE,
    MAX_PRICE_DECIMAL_PLACES,
)


# Giới hạn lưu trữ DECIMAL(12, 2)
MAX_MONEY_AMOUNT = MAX_TOUR_PRICE

MONEY_QUANTUM = Decimal("0.01")


def validate_money_amount(
    value: Decimal,
    *,
    allow_zero: bool = False,
) -> Decimal:

    # Kiểm tra kiểu dữ liệu
    if not isinstance(value, Decimal):
        raise ValueError(
            "Số tiền phải sử dụng kiểu Decimal"
        )

    # Không chấp nhận NaN hoặc Infinity
    if not value.is_finite():
        raise ValueError(
            "Số tiền phải là số hữu hạn"
        )

    # Kiểm tra số tiền âm
    if value < 0:
        raise ValueError(
            "Số tiền không được âm"
        )

    # Kiểm tra số tiền bằng 0
    if not allow_zero and value == 0:
        raise ValueError(
            "Số tiền phải lớn hơn 0"
        )

    # Kiểm tra giới hạn lưu trữ MySQL
    if value > MAX_MONEY_AMOUNT:
        raise ValueError(
            "Số tiền vượt quá giới hạn cho phép"
        )

    # Kiểm tra số chữ số thập phân
    digits = value.as_tuple().digits
    exponent = value.as_tuple().exponent

    if exponent < -MAX_PRICE_DECIMAL_PLACES:

        extra_places = (
            -exponent - MAX_PRICE_DECIMAL_PLACES
        )

        if any(digits[-extra_places:]):
            raise ValueError(
                "Số tiền chỉ được có tối đa "
                "2 chữ số thập phân"
            )

    # Chuẩn hóa về đúng 2 chữ số thập phân
    with localcontext() as ctx:
        ctx.prec = 28

        return value.quantize(MONEY_QUANTUM)


def calculate_booking_total(
    unit_price: Decimal,
    number_of_people: int,
) -> Decimal:

    # Kiểm tra đơn giá
    unit_price = validate_money_amount(
        unit_price
    )

    # Kiểm tra kiểu dữ liệu số lượng khách
    if type(number_of_people) is not int:
        raise ValueError(
            "Số lượng khách phải là số nguyên"
        )

    # Kiểm tra giới hạn số lượng khách
    if not (
        1 <= number_of_people
        <= MAX_BOOKING_PEOPLE
    ):
        raise ValueError(
            "Số lượng khách vượt quá "
            "giới hạn cho phép"
        )

    # Tính tổng tiền bằng Decimal
    with localcontext() as ctx:
        ctx.prec = 28

        total_amount = (
            unit_price * number_of_people
        )

    # Kiểm tra tổng tiền trước khi lưu MySQL
    return validate_money_amount(
        total_amount
    )
    
    
    

def validate_booking_amount(
    unit_price: Decimal,
    number_of_people: int,
    total_amount: Decimal,
) -> Decimal:

    # Kiểm tra tổng tiền đã lưu trong Booking
    stored_total = validate_money_amount(
        total_amount
    )

    # Tính lại tổng tiền từ dữ liệu Booking
    expected_total = calculate_booking_total(
        unit_price,
        number_of_people,
    )

    # Kiểm tra tính nhất quán
    if stored_total != expected_total:
        raise ValueError(
            "Tổng tiền Booking không nhất quán"
        )

    return stored_total

