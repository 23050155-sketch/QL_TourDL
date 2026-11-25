
import unicodedata


# 1. Kiểm tra ký tự điều khiển trong văn bản
def validate_text_characters(
    value,
    *,
    allow_line_breaks: bool = True,
    allow_tab: bool = True,
):

    # Giữ nguyên None và dữ liệu không phải chuỗi
    # Pydantic sẽ chịu trách nhiệm kiểm tra kiểu dữ liệu
    if not isinstance(value, str):
        return value

    for char in value:

        # Cho phép xuống dòng nếu được cấu hình
        if char in "\r\n" and allow_line_breaks:
            continue

        # Cho phép tab nếu được cấu hình
        if char == "\t" and allow_tab:
            continue

        # Kiểm tra nhóm ký tự Unicode
        category = unicodedata.category(char)

        # Cc: Control Character
        # Cs: Surrogate Character
        if category in ("Cc", "Cs"):
            raise ValueError(
                "Văn bản chứa ký tự không hợp lệ"
            )

    return value


# 2. Kiểm tra văn bản một dòng trước chuẩn hóa
def validate_single_line_text(value):

    return validate_text_characters(
        value,
        allow_line_breaks=True,
        allow_tab=True,
    )


# 3. Kiểm tra văn bản nhiều dòng
def validate_multiline_text(value):

    return validate_text_characters(
        value,
        allow_line_breaks=True,
        allow_tab=True,
    )


# 4. Kiểm tra mã định danh và mã giao dịch
def validate_identifier_text(value):

    return validate_text_characters(
        value,
        allow_line_breaks=False,
        allow_tab=False,
    )
