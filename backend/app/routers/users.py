
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
    # 1. Kiểm tra mật khẩu hiện tại
    if not verify_password(
        data.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu hiện tại không chính xác"
        )

    # 2. Kiểm tra xác nhận mật khẩu mới
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Xác nhận mật khẩu không khớp"
        )

    # 3. Không cho phép sử dụng lại mật khẩu hiện tại
    if verify_password(
        data.new_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Mật khẩu mới không được trùng mật khẩu hiện tại"
        )

    # 4. Băm mật khẩu mới
    current_user.password_hash = hash_password(
        data.new_password
    )

    # 5. Lưu thay đổi vào MySQL
    db.commit()

    return {
        "message": "Đổi mật khẩu thành công"
    }





# ADMIN xem danh sách khách hàng
@router.get(
    "/",
    response_model=UserListResponse
)
def get_customers(
    search: str | None = Query(
        default=None,
        max_length=150
    ),
    status: Literal["active", "inactive"] | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Chỉ lấy tài khoản CUSTOMER
    query = db.query(User).filter(
        User.role == "customer"
    )

    # Tìm kiếm theo tên, email hoặc số điện thoại
    if search and search.strip():
        keyword = search.strip()

        query = query.filter(
            or_(
                User.full_name.contains(
                    keyword, autoescape=True
                ),
                User.email.contains(
                    keyword, autoescape=True
                ),
                User.phone.contains(
                    keyword, autoescape=True
                )
            )
        )

    # Lọc theo trạng thái tài khoản
    if status is not None:
        query = query.filter(
            User.status == status
        )

    # Đếm tổng số bản ghi sau khi lọc
    total = query.count()

    # Tính tổng số trang
    total_pages = (
        total + page_size - 1
    ) // page_size

    # Tính số bản ghi cần bỏ qua
    offset = (page - 1) * page_size

    # Lấy dữ liệu theo trang
    customers = (
        query
        .order_by(User.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

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

    # Cập nhật trạng thái
    customer.status = data.status

    db.commit()
    db.refresh(customer)

    return customer

