from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Import FastAPI để xây dựng các API
from fastapi import FastAPI, HTTPException

# Cho phép Frontend ReactJS gọi API từ cổng khác
from fastapi.middleware.cors import CORSMiddleware

# Hàm kiểm tra kết nối MySQL
from app.database import test_connection

# Import các nhóm API quản lý tour và xác thực
from app.routers.tours import router as tours_router
from app.routers.auth import router as auth_router


from app.routers import tour_schedules
from app.routers import bookings
from app.routers import payments
from app.routers import destinations
from app.routers import tour_destinations
from app.routers import guides
from app.routers import guide_assignments
from app.routers import reviews
from app.routers import dashboard
from app.routers import users
from app.core.config import settings


from sqlalchemy.exc import SQLAlchemyError

from app.core.database_errors import (
    database_exception_handler
)


# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="HTTT16 - Quan Ly Tour Du Lich",
    version="1.0.0",
    description="RESTful API cho he thong quan ly tour du lich noi dia"
)



# Xử lý lỗi Database dùng chung
app.add_exception_handler(
    SQLAlchemyError,
    database_exception_handler,
)


# Bổ sung HTTP Security Headers
@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next
):

    # Tiếp tục xử lý Request
    response = await call_next(request)

    # Không cho trình duyệt tự suy đoán kiểu nội dung
    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    return response





# Xử lý lỗi kiểm tra dữ liệu đầu vào
# Không trả về dữ liệu nhạy cảm trong phản hồi lỗi
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():

        # Chuẩn hóa vị trí lỗi để đảm bảo JSON hợp lệ
        safe_loc = [
            part.encode(
                "utf-8",
                errors="backslashreplace"
            ).decode("utf-8")
            if isinstance(part, str)
            else part
            for part in error.get("loc", [])
        ]

        errors.append({
            "loc": safe_loc,
            "msg": "Dữ liệu đầu vào không hợp lệ",
            "type": error.get("type", "validation_error")
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": errors
        }
    )





# Cấu hình CORS để ReactJS truy cập Backend
app.add_middleware(
    CORSMiddleware,

    # Chỉ cho phép các Origin đã cấu hình
    allow_origins=settings.CORS_ORIGINS,

    # Sử dụng Bearer JWT, không dùng Cookie xác thực
    allow_credentials=False,

    # Chỉ cho phép các phương thức cần thiết
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    # Chỉ cho phép các Header cần thiết
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],

    # Cache kết quả Preflight trong 10 phút
    max_age=600,
)



# Đăng ký các API quản lý tour
app.include_router(tours_router)

# Đăng ký các API đăng ký, đăng nhập và JWT
app.include_router(auth_router)

app.include_router(tour_schedules.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(destinations.router)
app.include_router(tour_destinations.router)
app.include_router(guides.router)
app.include_router(guide_assignments.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)
app.include_router(users.router)


# API kiểm tra Backend có hoạt động không
@app.get("/")
def home():
    # API này không truy vấn MySQL
    return {
        "message": "HTTT16 Backend dang hoat dong"
    }


# API kiểm tra kết nối database
@app.get("/api/health")
def health():
    try:
        # Thử kết nối đến MySQL
        test_connection()

        # Kết nối thành công
        return {
            "status": "success",
            "database": "connected"
        }

    except Exception:
        # Trả HTTP 503 khi database không khả dụng
        raise HTTPException(
            status_code=503,
            detail="Khong the ket noi MySQL"
        )
