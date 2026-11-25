
from decimal import Decimal

from fastapi import HTTPException

from app.core.normalization import (
    normalize_optional_text,
)

from app.core.validation import (
    MAX_SEARCH_LENGTH,
    MAX_PAGE_SIZE,
    MAX_PAGE_NUMBER,
    MAX_PAGINATION_OFFSET,
    MAX_TOUR_PRICE,
    MAX_PRICE_DECIMAL_PLACES,
)


from app.core.text_validation import (
    validate_single_line_text,
)


from app.core.money_validation import (
    validate_money_amount,
)


# 1. Chuẩn hóa từ khóa tìm kiếm

def normalize_search_keyword(
    value: str | None,
    max_length: int = MAX_SEARCH_LENGTH
) -> str | None:

    if value is None:
        return None

    if not isinstance(value, str):
        raise HTTPException(
            status_code=422,
            detail="Từ khóa tìm kiếm phải là chuỗi"
        )

    # Kiểm tra độ dài trước chuẩn hóa
    if len(value) > max_length:
        raise HTTPException(
            status_code=422,
            detail=(
                "Từ khóa tìm kiếm vượt quá "
                "độ dài cho phép"
            )
        )

    # Kiểm tra và chuẩn hóa văn bản
    try:
        value = validate_single_line_text(value)

        keyword = normalize_optional_text(value)

    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Từ khóa chứa ký tự không hợp lệ"
        ) from None

    # Kiểm tra độ dài sau chuẩn hóa
    if (
        keyword is not None
        and len(keyword) > max_length
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Từ khóa tìm kiếm vượt quá "
                "độ dài cho phép"
            )
        )

    return keyword



# 2. Kiểm tra khoảng giá tìm kiếm

def validate_price_range(
    min_price: Decimal | None,
    max_price: Decimal | None,
) -> tuple[Decimal | None, Decimal | None]:

    # Kiểm tra và chuẩn hóa giá tối thiểu
    if min_price is not None:
        try:
            min_price = validate_money_amount(
                min_price,
                allow_zero=True,
            )

        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Giá tối thiểu không hợp lệ",
            ) from None

    # Kiểm tra và chuẩn hóa giá tối đa
    if max_price is not None:
        try:
            max_price = validate_money_amount(
                max_price,
                allow_zero=True,
            )

        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Giá tối đa không hợp lệ",
            ) from None

    # Kiểm tra khoảng giá
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Giá tối thiểu không được "
                "lớn hơn giá tối đa"
            ),
        )

    return min_price, max_price



# 3. Kiểm tra phân trang và trả về OFFSET
def validate_pagination(
    page: int,
    page_size: int,
) -> int:

    if type(page) is not int:
        raise HTTPException(
            status_code=422,
            detail="Số trang phải là số nguyên"
        )

    if type(page_size) is not int:
        raise HTTPException(
            status_code=422,
            detail="Kích thước trang phải là số nguyên"
        )

    if page < 1 or page > MAX_PAGE_NUMBER:
        raise HTTPException(
            status_code=422,
            detail="Số trang vượt quá giới hạn cho phép"
        )

    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise HTTPException(
            status_code=422,
            detail="Kích thước trang vượt quá giới hạn cho phép"
        )

    offset = (page - 1) * page_size

    if offset > MAX_PAGINATION_OFFSET:
        raise HTTPException(
            status_code=422,
            detail="Phạm vi phân trang vượt quá giới hạn cho phép"
        )

    return offset


# 4. Tính tổng số trang
def calculate_total_pages(
    total: int,
    page_size: int,
) -> int:

    if type(total) is not int or total < 0:
        raise ValueError(
            "Tổng số bản ghi phải là số nguyên không âm"
        )

    if (
        type(page_size) is not int
        or not 1 <= page_size <= MAX_PAGE_SIZE
    ):
        raise ValueError(
            "Kích thước trang không hợp lệ"
        )

    return (total + page_size - 1) // page_size
