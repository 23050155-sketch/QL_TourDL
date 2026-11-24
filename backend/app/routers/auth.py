import jwt

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from app.core.rate_limiter import login_rate_limiter
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
    verify_login_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

from app.services.user_security import (
    lock_user,
    revoke_user_tokens
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
    request: Request,
    db: Session = Depends(get_db)
):

    # Lấy địa chỉ IP của Client
    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    # Kiểm tra giới hạn trước khi truy vấn MySQL
    login_rate_limiter.check(client_ip)

    # Chuẩn hóa email
    email = str(data.email).lower()

    # Tìm tài khoản
    user = db.query(User).filter(
        User.email == email
    ).first()

    # Lấy mật khẩu băm
    stored_hash = (
        user.password_hash
        if user is not None
        else None
    )

    # Kiểm tra mật khẩu
    password_valid = verify_login_password(
        data.password,
        stored_hash
    )

    # Kiểm tra thông tin xác thực
    if (
        user is None
        or not password_valid
        or user.status != "active"
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin đăng nhập không hợp lệ",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Tạo JWT
    token = create_access_token(
        user_id=user.id,
        token_version=user.token_version
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }





# Xác thực JWT và lấy tài khoản hiện tại
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    # Thông báo lỗi xác thực chung
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hiệu lực",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        # Giải mã và xác thực JWT
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require": [
                    "sub",
                    "type",
                    "ver",
                    "iat",
                    "exp"
                ]
            }
        )

        # Kiểm tra loại Token
        if payload["type"] != "access":
            raise jwt.InvalidTokenError()

        # Lấy ID tài khoản
        user_id = int(payload["sub"])

        if not 1 <= user_id <= 2**64 - 1:
            raise jwt.InvalidTokenError()

        # Lấy phiên bản Token
        token_version = payload["ver"]

        # Kiểm tra kiểu và phạm vi phiên bản
        if (
            type(token_version) is not int
            or not 1 <= token_version <= 2**32 - 1
        ):
            raise jwt.InvalidTokenError()

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError
    ):

        raise credentials_exception

    # Truy vấn tài khoản trong MySQL
    user = db.get(User, user_id)

    # Kiểm tra tài khoản tồn tại
    if user is None:
        raise credentials_exception

    # Kiểm tra trạng thái tài khoản
    if user.status != "active":
        raise credentials_exception

    # Kiểm tra phiên bản JWT
    if user.token_version != token_version:
        raise credentials_exception

    # Trả về tài khoản đã xác thực
    return user



# Trả về thông tin tài khoản hiện tại sau khi xác thực JWT
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user



# Đăng xuất và thu hồi toàn bộ JWT của tài khoản
@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Lưu phiên bản Token đã được xác thực
    authenticated_version = current_user.token_version

    # Khóa bản ghi tài khoản
    user = lock_user(
        db,
        current_user.id
    )

    # Kiểm tra lại trạng thái và phiên bản Token
    if (
        user is None
        or user.status != "active"
        or user.token_version != authenticated_version
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên đăng nhập không còn hợp lệ",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Thu hồi toàn bộ JWT cũ
    revoke_user_tokens(user)

    # Lưu thay đổi vào MySQL
    db.commit()

    return {
        "message": "Đăng xuất thành công",
        "require_login": True
    }



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



# Kiểm tra người dùng có quyền CUSTOMER hay không
def require_customer(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Chỉ khách hàng mới được thực hiện chức năng này"
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
