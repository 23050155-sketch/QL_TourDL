
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.destination import Destination, TourDestination
from app.models.user import User
from app.routers.auth import require_admin
from app.schemas.destination import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
)


router = APIRouter(
    prefix="/api/destinations",
    tags=["Destinations"],
)


# 1. Xem danh sách địa điểm
@router.get(
    "/",
    response_model=list[DestinationResponse],
)
def get_destinations(
    db: Session = Depends(get_db),
):
    return (
        db.query(Destination)
        .order_by(Destination.id.desc())
        .all()
    )


# 2. Xem chi tiết địa điểm
@router.get(
    "/{destination_id}",
    response_model=DestinationResponse,
)
def get_destination_detail(
    destination_id: int,
    db: Session = Depends(get_db),
):
    destination = db.get(Destination, destination_id)

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy địa điểm du lịch",
        )

    return destination


# 3. ADMIN thêm địa điểm
@router.post(
    "/",
    response_model=DestinationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_destination(
    data: DestinationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    destination = Destination(
        **data.model_dump()
    )

    db.add(destination)
    db.commit()
    db.refresh(destination)

    return destination


# 4. ADMIN cập nhật địa điểm
@router.put(
    "/{destination_id}",
    response_model=DestinationResponse,
)
def update_destination(
    destination_id: int,
    data: DestinationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    destination = db.get(Destination, destination_id)

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy địa điểm du lịch",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Không cho cập nhật name và province thành NULL
    for field in ("name", "province"):
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} không được để trống",
            )

    for field, value in update_data.items():
        setattr(destination, field, value)

    db.commit()
    db.refresh(destination)

    return destination


# 5. ADMIN xóa địa điểm
@router.delete(
    "/{destination_id}",
)
def delete_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    destination = db.get(Destination, destination_id)

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy địa điểm du lịch",
        )

    # Không xóa nếu địa điểm đang được sử dụng trong Tour
    is_used = (
        db.query(TourDestination)
        .filter(
            TourDestination.destination_id == destination_id
        )
        .first()
    )

    if is_used:
        raise HTTPException(
            status_code=409,
            detail="Địa điểm đang thuộc một Tour, không thể xóa",
        )

    db.delete(destination)
    db.commit()

    return {
        "message": "Xóa địa điểm thành công",
        "id": destination_id,
    }
