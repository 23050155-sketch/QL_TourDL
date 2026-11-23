
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tour import Tour
from app.models.user import User
from app.schemas.tour import TourCreate, TourUpdate, TourResponse
from app.routers.auth import require_admin

from app.models.tour_schedule import TourSchedule
from app.schemas.tour_schedule import TourScheduleResponse
from datetime import date

router = APIRouter(
    prefix="/api/tours",
    tags=["Tours"]
)


# Lấy danh sách tour đang hoạt động cho khách hàng
@router.get("/", response_model=list[TourResponse])
def get_tours(db: Session = Depends(get_db)):
    return (
        db.query(Tour)
        .filter(Tour.status == "active")
        .order_by(Tour.id.desc())
        .all()
    )


# ADMIN lấy toàn bộ tour, bao gồm tour đã ngừng kinh doanh
@router.get("/admin/all", response_model=list[TourResponse])
def get_all_tours(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return db.query(Tour).order_by(Tour.id.desc()).all()


# Xem thông tin chi tiết tour đang hoạt động
@router.get("/{tour_id}", response_model=TourResponse)
def get_tour_detail(
    tour_id: int,
    db: Session = Depends(get_db)
):
    tour = (
        db.query(Tour)
        .filter(
            Tour.id == tour_id,
            Tour.status == "active"
        )
        .first()
    )

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    return tour


# ADMIN tạo tour mới
@router.post(
    "/",
    response_model=TourResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tour(
    data: TourCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = Tour(**data.model_dump(), status="active")

    db.add(tour)
    db.commit()
    db.refresh(tour)

    return tour


# ADMIN cập nhật thông tin tour
@router.put("/{tour_id}", response_model=TourResponse)
def update_tour(
    tour_id: int,
    data: TourUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    for field, value in data.model_dump().items():
        setattr(tour, field, value)

    db.commit()
    db.refresh(tour)

    return tour


# ADMIN ngừng kinh doanh tour bằng cách cập nhật trạng thái
@router.delete("/{tour_id}")
def delete_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    tour.status = "inactive"
    db.commit()

    return {"message": "Đã ngừng kinh doanh tour thành công"}






# Lấy lịch khởi hành đang mở của một Tour
@router.get(
    "/{tour_id}/departures",
    response_model=list[TourScheduleResponse],
)
def get_tour_departures(
    tour_id: int,
    db: Session = Depends(get_db),
):
    tour = db.get(Tour, tour_id)

    if not tour or tour.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour đang hoạt động",
        )

    return (
        db.query(TourSchedule)
        .filter(
            TourSchedule.tour_id == tour_id,
            TourSchedule.status == "open",
            TourSchedule.departure_date >= date.today(),
        )
        .order_by(TourSchedule.departure_date.asc())
        .all()
    )

