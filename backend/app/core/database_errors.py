
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, DBAPIError


logger = logging.getLogger(__name__)


# Mã lỗi MySQL
MYSQL_DUPLICATE_ENTRY = 1062
MYSQL_LOCK_WAIT_TIMEOUT = 1205
MYSQL_DEADLOCK = 1213


# Lấy mã lỗi từ MySQL Driver
def get_mysql_error_code(
    exc: SQLAlchemyError
) -> int | None:

    if not isinstance(exc, DBAPIError):
        return None

    original_error = exc.orig
    args = getattr(original_error, "args", ())

    if not args:
        return None

    error_code = args[0]

    if type(error_code) is int:
        return error_code

    return None


# Xử lý lỗi Database dùng chung
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:

    error_code = get_mysql_error_code(exc)

    # Deadlock
    if error_code == MYSQL_DEADLOCK:
        return JSONResponse(
            status_code=409,
            content={
                "detail": (
                    "Dữ liệu đang được xử lý bởi "
                    "một yêu cầu khác. "
                    "Vui lòng kiểm tra lại và thử lại."
                )
            },
        )

    # Lock Wait Timeout
    if error_code == MYSQL_LOCK_WAIT_TIMEOUT:
        return JSONResponse(
            status_code=503,
            content={
                "detail": (
                    "Hệ thống đang bận xử lý dữ liệu. "
                    "Vui lòng kiểm tra lại sau."
                )
            },
            headers={
                "Retry-After": "2"
            },
        )

    # Duplicate Entry
    if error_code == MYSQL_DUPLICATE_ENTRY:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Dữ liệu đã tồn tại hoặc bị trùng lặp"
            },
        )

    # Ghi log an toàn, không ghi dữ liệu SQL
    logger.error(
        "Database error: type=%s, code=%s",
        type(exc).__name__,
        error_code,
    )

    # Không trả lỗi SQL chi tiết cho Client
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Đã xảy ra lỗi khi xử lý dữ liệu"
        },
    )
