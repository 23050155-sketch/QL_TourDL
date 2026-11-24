
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.guide import TourGuide, GuideAssignment
from app.models.user import User
from app.routers.auth import require_admin
from app.schemas.guide import (
    GuideCreate,
    GuideUpdate,
    GuideResponse,
    GuidePublicResponse,
)


router = APIRouter(
    prefix="/api/guides",
    tags=["Tour Guides"],
)



# 1. Xem danh sách hướng dẫn viên công khai
@router.get(
    "/",
    response_model=list[GuidePublicResponse],
)
def get_guides(
    db: Session = Depends(get_db),
):
    return (
        db.query(TourGuide)
        .filter(TourGuide.status == "active")
        .order_by(TourGuide.id.desc())
        .all()
    )




# ADMIN xem toàn bộ hướng dẫn viên
@router.get(
    "/admin/all",
    response_model=list[GuideResponse],
)
def get_all_guides(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(TourGuide)
        .order_by(TourGuide.id.desc())
        .all()
    )




# ADMIN xem chi tiết hướng dẫn viên
@router.get(
    "/admin/{guide_id}",
    response_model=GuideResponse,
)
def admin_get_guide_detail(
    guide_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    guide = db.get(TourGuide, guide_id)

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hướng dẫn viên",
        )

    return guide





# 2. Xem chi tiết hướng dẫn viên công khai
@router.get(
    "/{guide_id}",
    response_model=GuidePublicResponse,
)
def get_guide_detail(
    guide_id: int,
    db: Session = Depends(get_db),
):
    guide = (
        db.query(TourGuide)
        .filter(
            TourGuide.id == guide_id,
            TourGuide.status == "active",
        )
        .first()
    )

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hướng dẫn viên đang hoạt động",
        )

    return guide



# 3. ADMIN thêm hướng dẫn viên
@router.post(
    "/",
    response_model=GuideResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guide(
    data: GuideCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    guide = TourGuide(**data.model_dump())

    db.add(guide)

    try:
        db.commit()
        db.refresh(guide)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email hướng dẫn viên đã tồn tại",
        )

    return guide


# 4. ADMIN cập nhật hướng dẫn viên
@router.put(
    "/{guide_id}",
    response_model=GuideResponse,
)
def update_guide(
    guide_id: int,
    data: GuideUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    guide = db.get(TourGuide, guide_id)

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hướng dẫn viên",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Không cho phép các trường bắt buộc nhận NULL
    for field in ("full_name", "status"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} không được để trống",
            )

    for field, value in update_data.items():
        setattr(guide, field, value)

    try:
        db.commit()
        db.refresh(guide)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email hướng dẫn viên đã tồn tại",
        )

    return guide


# 5. ADMIN xóa hướng dẫn viên
@router.delete("/{guide_id}")
def delete_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    guide = db.get(TourGuide, guide_id)

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hướng dẫn viên",
        )

    # Kiểm tra hướng dẫn viên đã được phân công chưa
    assignment = (
        db.query(GuideAssignment)
        .filter(GuideAssignment.guide_id == guide_id)
        .first()
    )

    if assignment:
        raise HTTPException(
            status_code=409,
            detail=(
                "Hướng dẫn viên đã được phân công "
                "cho lịch khởi hành, không thể xóa"
            ),
        )

    db.delete(guide)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Không thể xóa hướng dẫn viên do ràng buộc dữ liệu",
        )

    return {
        "message": "Xóa hướng dẫn viên thành công",
        "id": guide_id,
    }
