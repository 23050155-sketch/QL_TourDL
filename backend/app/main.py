
# Import FastAPI để xây dựng các API
from fastapi import FastAPI, HTTPException

# Cho phép Frontend ReactJS gọi API từ cổng khác
from fastapi.middleware.cors import CORSMiddleware

# Hàm kiểm tra kết nối MySQL
from app.database import test_connection

# Import các nhóm API quản lý tour và xác thực
from app.routers.tours import router as tours_router
from app.routers.auth import router as auth_router


# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="HTTT16 - Quan Ly Tour Du Lich",
    version="1.0.0",
    description="RESTful API cho he thong quan ly tour du lich noi dia"
)


# Cấu hình CORS để ReactJS truy cập Backend
app.add_middleware(
    CORSMiddleware,

    # Địa chỉ Frontend Vite
    allow_origins=["http://localhost:5173"],

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
