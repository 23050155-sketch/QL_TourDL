
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tour import Tour
from app.models.tour_schedule import TourSchedule
from app.models.user import User
from app.schemas.tour_schedule import (
    TourScheduleCreate,
    TourScheduleUpdate,
    TourScheduleResponse,
)
from app.routers.auth import require_admin


router = APIRouter(prefix="/api/departures", tags=["Tour Schedules"])


# Lấy danh sách lịch khởi hành đang mở
@router.get("/", response_model=list[TourScheduleResponse])
def get_departures(db: Session = Depends(get_db)):
    return (
        db.query(TourSchedule)
        .join(Tour, Tour.id == TourSchedule.tour_id)
        .filter(
            TourSchedule.status == "open",
            Tour.status == "active",
            TourSchedule.departure_date >= date.today(),
        )
        .order_by(TourSchedule.departure_date.asc())
        .all()
    )


# ADMIN xem toàn bộ lịch khởi hành
@router.get("/admin/all", response_model=list[TourScheduleResponse])
def get_all_departures(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(TourSchedule)
        .order_by(TourSchedule.id.desc())
        .all()
    )


# Lấy chi tiết lịch khởi hành đang mở
@router.get("/{schedule_id}", response_model=TourScheduleResponse)
def get_departure_detail(
    schedule_id: int,
    db: Session = Depends(get_db),
):
    schedule = (
        db.query(TourSchedule)
        .join(Tour, Tour.id == TourSchedule.tour_id)
        .filter(
            TourSchedule.id == schedule_id,
            TourSchedule.status == "open",
            Tour.status == "active",
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành đang mở",
        )

    return schedule


# ADMIN thêm lịch khởi hành
@router.post(
    "/",
    response_model=TourScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_departure(
    data: TourScheduleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    tour = db.get(Tour, data.tour_id)

    if not tour or tour.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Tour không tồn tại hoặc đã ngừng kinh doanh",
        )

    if data.departure_date < date.today():
        raise HTTPException(
            status_code=422,
            detail="Ngày khởi hành không được ở trong quá khứ",
        )

    schedule = TourSchedule(
        **data.model_dump(),
        status="open",
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


# ADMIN cập nhật lịch khởi hành
@router.put("/{schedule_id}", response_model=TourScheduleResponse)
def update_departure(
    schedule_id: int,
    data: TourScheduleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    schedule = db.get(TourSchedule, schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành",
        )

    tour = db.get(Tour, data.tour_id)

    if not tour or tour.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Tour không tồn tại hoặc đã ngừng kinh doanh",
        )

    if data.status == "open" and data.departure_date < date.today():
        raise HTTPException(
            status_code=422,
            detail="Không thể mở lịch khởi hành trong quá khứ",
        )

    for field, value in data.model_dump().items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return schedule


# ADMIN hủy lịch khởi hành
@router.delete("/{schedule_id}")
def cancel_departure(
    schedule_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    schedule = db.get(TourSchedule, schedule_id)

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành",
        )

    schedule.status = "cancelled"
    db.commit()

    return {"message": "Đã hủy lịch khởi hành thành công"}
