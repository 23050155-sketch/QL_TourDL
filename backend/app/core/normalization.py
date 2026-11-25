
import re
import unicodedata

from pydantic import HttpUrl, TypeAdapter, ValidationError

from app.core.text_validation import (
    validate_single_line_text,
    validate_multiline_text,
    validate_identifier_text,
)


# Chuẩn hóa Unicode tiếng Việt
def normalize_unicode(value):
    if not isinstance(value, str):
        return value

    return unicodedata.normalize("NFC", value)


# Chuẩn hóa chuỗi văn bản một dòng
def normalize_single_line(value):

    if not isinstance(value, str):
        return value

    # Kiểm tra ký tự trước khi chuẩn hóa
    value = validate_single_line_text(value)

    # Chuẩn hóa Unicode
    value = normalize_unicode(value)

    # Chuẩn hóa khoảng trắng thành một dòng
    value = " ".join(value.split())

    return value


# Chuẩn hóa chuỗi văn bản nhiều dòng
def normalize_multiline(value):

    if not isinstance(value, str):
        return value

    # Kiểm tra ký tự văn bản
    value = validate_multiline_text(value)

    # Chuẩn hóa Unicode
    value = normalize_unicode(value)

    # Chuẩn hóa ký tự xuống dòng
    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")

    # Xóa khoảng trắng cuối mỗi dòng
    lines = [
        line.rstrip()
        for line in value.split("\n")
    ]

    value = "\n".join(lines)

    return value.strip()


# Chuẩn hóa chuỗi tùy chọn một dòng
def normalize_optional_text(value):
    value = normalize_single_line(value)

    if isinstance(value, str) and value == "":
        return None

    return value


# Chuẩn hóa văn bản tùy chọn nhiều dòng
def normalize_optional_multiline(value):
    value = normalize_multiline(value)

    if isinstance(value, str) and value == "":
        return None

    return value


# Chuẩn hóa email
def normalize_email(value):

    if not isinstance(value, str):
        return value

    # Không cho phép ký tự điều khiển
    value = validate_identifier_text(value)

    return value.strip().lower()


# Chuẩn hóa số điện thoại
def normalize_phone(value):

    if not isinstance(value, str):
        return value

    # Kiểm tra ký tự điều khiển
    value = validate_identifier_text(value)

    value = value.strip()

    if value == "":
        return None

    # Loại bỏ ký tự phân cách hợp lệ
    value = re.sub(
        r"[\s().-]+",
        "",
        value
    )

    return value


# Kiểm tra định dạng số điện thoại
def validate_phone_format(value):
    if value is None:
        return value

    if not isinstance(value, str):
        raise ValueError(
            "Số điện thoại phải là chuỗi"
        )

    # Cho phép dấu + ở đầu và từ 7 đến 15 chữ số
    if not re.fullmatch(r"\+?[0-9]{7,15}", value):
        raise ValueError(
            "Số điện thoại không đúng định dạng"
        )

    return value


# Chuẩn hóa URL tùy chọn

def normalize_optional_url(value):

    if not isinstance(value, str):
        return value

    # Kiểm tra ký tự trước khi loại bỏ khoảng trắng
    value = validate_identifier_text(value)

    # Loại bỏ khoảng trắng ở hai đầu
    value = value.strip()

    # Chuyển chuỗi rỗng thành None
    if value == "":
        return None

    return value



# Chuẩn hóa mã giao dịch
def normalize_transaction_code(value):

    if not isinstance(value, str):
        return value

    # Không cho phép ký tự điều khiển,
    # tab hoặc xuống dòng
    value = validate_identifier_text(value)

    value = value.strip()

    if value == "":
        return None

    return value




# Bộ kiểm tra URL HTTP/HTTPS
_image_url_adapter = TypeAdapter(HttpUrl)


# Kiểm tra định dạng URL hình ảnh

def validate_image_url(value):

    if value is None:
        return value

    if not isinstance(value, str):
        raise ValueError(
            "URL hình ảnh phải là chuỗi"
        )

    # Kiểm tra ký tự điều khiển và surrogate
    value = validate_identifier_text(value)

    # Không cho phép khoảng trắng bên trong URL
    if any(char.isspace() for char in value):
        raise ValueError(
            "URL hình ảnh chứa khoảng trắng không hợp lệ"
        )

    # Không cho phép dấu gạch chéo ngược
    if "\\" in value:
        raise ValueError(
            "URL hình ảnh không được chứa dấu gạch chéo ngược"
        )

    # Chỉ chấp nhận HTTP và HTTPS
    if not value.lower().startswith(
        ("http://", "https://")
    ):
        raise ValueError(
            "URL hình ảnh phải sử dụng HTTP hoặc HTTPS"
        )

    # Kiểm tra URL có phần địa chỉ máy chủ
    authority = value.split("://", 1)[1]

    if not authority or authority.startswith(
        ("/", "?", "#")
    ):
        raise ValueError(
            "URL hình ảnh không có địa chỉ máy chủ hợp lệ"
        )

    # Kiểm tra định dạng URL bằng Pydantic
    try:
        parsed_url = _image_url_adapter.validate_python(
            value
        )

    except ValidationError:
        raise ValueError(
            "URL hình ảnh không đúng định dạng"
        ) from None

    # Kiểm tra hostname
    if not parsed_url.host:
        raise ValueError(
            "URL hình ảnh không có hostname"
        )

    # Không cho phép thông tin đăng nhập trong URL
    if (
        parsed_url.username is not None
        or parsed_url.password is not None
    ):
        raise ValueError(
            "URL hình ảnh không được chứa thông tin đăng nhập"
        )

    # Giữ nguyên URL sau khi đã kiểm tra
    return value

