import jwt

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

bearer_scheme = HTTPBearer()


# Đăng ký tài khoản mới; tài khoản mặc định có quyền CUSTOMER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = str(data.email).lower()

    # Kiểm tra email đã tồn tại để tránh đăng ký trùng
    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email đã được sử dụng"
        )

    user = User(
        full_name=data.full_name.strip(),
        email=email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        role="customer",
        status="active"
    )

    # Lưu tài khoản mới vào cơ sở dữ liệu
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Không thể tạo tài khoản. Hãy kiểm tra email."
        )

    return user


# Xác thực email, mật khẩu và cấp JWT cho tài khoản hợp lệ
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    email = str(data.email).lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if (
        user is None
        or not verify_password(
            data.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị vô hiệu hóa"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Giải mã JWT và lấy tài khoản đang đăng nhập từ cơ sở dữ liệu
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        # Xác minh chữ ký, thời hạn và các trường bắt buộc của JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp"]}
        )

        if payload.get("type") != "access":
            raise jwt.InvalidTokenError()

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.get(User, user_id)

    if user is None or user.status != "active":
        raise HTTPException(
            status_code=401,
            detail="Tài khoản không tồn tại hoặc không hoạt động"
        )

    return user


# Trả về thông tin tài khoản hiện tại sau khi xác thực JWT
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user


# Kiểm tra người dùng có quyền ADMIN hay không
def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền quản trị"
        )

    return current_user


# API thử nghiệm chức năng phân quyền ADMIN
@router.get("/admin-test")
def admin_test(
    admin: User = Depends(require_admin)
):
    return {
        "message": "Truy cập quản trị thành công",
        "admin_id": admin.id
    }
