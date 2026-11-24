
import secrets

from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash

from app.core.config import settings


# Cấu hình JWT
SECRET_KEY = settings.JWT_SECRET_KEY

ALGORITHM = settings.JWT_ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)


# Khởi tạo cơ chế băm mật khẩu
password_hash = PasswordHash.recommended()


# Tạo mật khẩu băm giả một lần khi Backend khởi động
DUMMY_PASSWORD_HASH = password_hash.hash(
    secrets.token_urlsafe(32)
)


# Băm mật khẩu
def hash_password(password: str) -> str:

    return password_hash.hash(password)


# Kiểm tra mật khẩu
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


# Kiểm tra mật khẩu trong quá trình đăng nhập
def verify_login_password(
    plain_password: str,
    hashed_password: str | None
) -> bool:

    if hashed_password is None:

        verify_password(
            plain_password,
            DUMMY_PASSWORD_HASH
        )

        return False

    return verify_password(
        plain_password,
        hashed_password
    )



# Tạo JWT Access Token
def create_access_token(
    user_id: int,
    token_version: int
) -> str:

    # Thời điểm phát hành Token
    now = datetime.now(timezone.utc)

    # Thời điểm hết hạn Token
    expire = now + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Nội dung JWT
    payload = {
        "sub": str(user_id),
        "type": "access",
        "ver": token_version,
        "iat": now,
        "exp": expire
    }

    # Ký JWT bằng Secret Key
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

