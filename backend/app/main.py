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


# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="HTTT16 - Quan Ly Tour Du Lich",
    version="1.0.0",
    description="RESTful API cho he thong quan ly tour du lich noi dia"
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

        errors.append({
            "loc": error.get("loc", []),
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

    # Địa chỉ Frontend Vite
    allow_origins=settings.CORS_ORIGINS,

    # Cho phép gửi thông tin xác thực khi cần
    allow_credentials=True,

    # Cho phép các phương thức GET, POST, PUT, DELETE...
    allow_methods=["*"],

    # Cho phép gửi các HTTP header, bao gồm Authorization
    allow_headers=["*"]
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
