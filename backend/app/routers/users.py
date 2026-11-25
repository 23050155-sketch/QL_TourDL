
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

from typing import Literal
from sqlalchemy import or_

from app.schemas.auth import UserResponse
from app.schemas.user import (
    ProfileUpdate,
    ChangePasswordRequest,
    UserStatusUpdate,
    UserListResponse
)

from app.core.security import (
    hash_password,
    verify_password
)

from app.routers.auth import (
    get_current_user,
    require_admin
)

from app.services.user_security import (
    lock_user,
    revoke_user_tokens
)



from app.core.validation import (
    MAX_USER_SEARCH_LENGTH,
    MAX_PAGE_SIZE,
    MAX_PAGE_NUMBER,
)

from app.core.search_validation import (
    normalize_search_keyword,
    validate_pagination,
    calculate_total_pages,
)



router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# Cập nhật thông tin tài khoản cá nhân
@router.put(
    "/me",
    response_model=UserResponse
)
def update_my_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cập nhật họ tên
    current_user.full_name = data.full_name

    # Cập nhật số điện thoại
    current_user.phone = data.phone

    # Lưu thay đổi vào MySQL
    db.commit()

    # Lấy lại dữ liệu mới nhất
    db.refresh(current_user)

    return current_user




# Đổi mật khẩu tài khoản cá nhân

@router.put("/me/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Lưu phiên bản đã được xác thực
    authenticated_version = current_user.token_version

    # Khóa bản ghi tài khoản
    user = lock_user(
        db,
        current_user.id
    )

    # Kiểm tra lại trạng thái và phiên bản
    if (
        user is None
        or user.status != "active"
        or user.token_version != authenticated_version
    ):

        raise HTTPException(
            status_code=401,
            detail="Phiên đăng nhập không còn hợp lệ",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Kiểm tra mật khẩu hiện tại
    if not verify_password(
        data.current_password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=400,
            detail="Mật khẩu hiện tại không chính xác"
        )

    # Kiểm tra xác nhận mật khẩu
    if data.new_password != data.confirm_password:

        raise HTTPException(
            status_code=400,
            detail="Xác nhận mật khẩu không khớp"
        )

    # Không cho phép sử dụng lại mật khẩu hiện tại
    if verify_password(
        data.new_password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Mật khẩu mới không được trùng "
                "mật khẩu hiện tại"
            )
        )

    # Băm mật khẩu mới
    user.password_hash = hash_password(
        data.new_password
    )

    # Thu hồi tất cả JWT cũ
    revoke_user_tokens(user)

    # Lưu cả mật khẩu và phiên bản Token
    db.commit()

    return {
        "message": "Đổi mật khẩu thành công",
        "require_login": True
    }






# ADMIN xem danh sách khách hàng
@router.get(
    "/",
    response_model=UserListResponse
)
def get_customers(
    search: str | None = Query(
        default=None,
        max_length=MAX_USER_SEARCH_LENGTH
    ),
    status: Literal[
        "active",
        "inactive"
    ] | None = None,
    page: int = Query(
        default=1,
        ge=1,
        le=MAX_PAGE_NUMBER
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=MAX_PAGE_SIZE
    ),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):

    # 1. Kiểm tra phân trang
    offset = validate_pagination(
        page,
        page_size
    )

    # 2. Chuẩn hóa từ khóa tìm kiếm
    keyword = normalize_search_keyword(
        search,
        max_length=MAX_USER_SEARCH_LENGTH
    )

    # 3. Chỉ lấy tài khoản CUSTOMER
    query = db.query(User).filter(
        User.role == "customer"
    )

    # 4. Tìm kiếm theo họ tên, email và số điện thoại
    if keyword is not None:
        query = query.filter(
            or_(
                User.full_name.contains(
                    keyword,
                    autoescape=True
                ),
                User.email.contains(
                    keyword,
                    autoescape=True
                ),
                User.phone.contains(
                    keyword,
                    autoescape=True
                )
            )
        )

    # 5. Lọc theo trạng thái tài khoản
    if status is not None:
        query = query.filter(
            User.status == status
        )

    # 6. Đếm tổng số bản ghi sau khi lọc
    total = query.count()

    # 7. Tính tổng số trang
    total_pages = calculate_total_pages(
        total,
        page_size
    )

    # 8. Lấy dữ liệu theo trang
    customers = (
        query
        .order_by(User.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 9. Trả về kết quả
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": customers
    }






# ADMIN xem chi tiết khách hàng
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_customer_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    customer = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.role == "customer"
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy khách hàng"
        )

    return customer





# ADMIN cập nhật trạng thái khách hàng

@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_customer_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):

    # Khóa bản ghi tài khoản cần cập nhật
    customer = lock_user(
        db,
        user_id
    )

    # Chỉ cho phép quản lý CUSTOMER
    if (
        customer is None
        or customer.role != "customer"
    ):

        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy khách hàng"
        )

    # Chỉ cập nhật khi trạng thái thay đổi
    if customer.status != data.status:

        customer.status = data.status

        # Thu hồi toàn bộ JWT cũ
        revoke_user_tokens(customer)

    # Lưu thay đổi
    db.commit()

    db.refresh(customer)

    return customer


