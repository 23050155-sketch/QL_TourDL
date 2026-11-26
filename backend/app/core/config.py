
import os
from pathlib import Path

from dotenv import load_dotenv
from urllib.parse import urlsplit


# Xác định thư mục gốc Backend
BASE_DIR = Path(__file__).resolve().parents[2]

# Đọc file .env từ thư mục Backend
load_dotenv(BASE_DIR / ".env")


class Settings:

    # Cấu hình MySQL
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv(
        "DB_NAME",
        "quan_ly_tour_du_lich"
    )

    # Cấu hình JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "30"
        )
    )

    # Cấu hình CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173"
        ).split(",")
        if origin.strip()
    ]

    def __init__(self):

        # Kiểm tra JWT Secret Key
        if len(self.JWT_SECRET_KEY.encode("utf-8")) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY phai co it nhat 32 byte"
            )

        # Kiểm tra thời hạn Token
        if not 1 <= self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES <= 1440:
            raise RuntimeError(
                "Thoi han JWT phai tu 1 den 1440 phut"
            )

        # Kiểm tra cổng MySQL
        if not 1 <= self.DB_PORT <= 65535:
            raise RuntimeError(
                "DB_PORT khong hop le"
            )

        
        # Kiểm tra cấu hình CORS
        if not self.CORS_ORIGINS or "*" in self.CORS_ORIGINS:
            raise RuntimeError(
                "CORS_ORIGINS khong hop le"
            )

        # Kiểm tra từng Origin
        for origin in self.CORS_ORIGINS:

            try:
                parsed = urlsplit(origin)

                if (
                    parsed.scheme not in ("http", "https")
                    or not parsed.hostname
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                    or "*" in origin
                    or "\\" in origin
                    or "?" in origin
                    or "#" in origin
                    or any(
                        char.isspace() or ord(char) < 32
                        for char in origin
                    )
                    or (
                        parsed.port is not None
                        and not 1 <= parsed.port <= 65535
                    )
                ):
                    raise ValueError()

            except ValueError:
                raise RuntimeError(
                    "CORS_ORIGINS chua Origin khong hop le"
                ) from None



# Khởi tạo cấu hình dùng chung
settings = Settings()
