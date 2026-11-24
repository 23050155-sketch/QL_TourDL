
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tour import Tour
from app.models.tour_schedule import TourSchedule
from app.models.user import User
from app.models.booking import Booking

from app.schemas.tour_schedule import (
    TourScheduleCreate,
    TourScheduleUpdate,
    TourScheduleResponse,
)
from app.routers.auth import require_admin

from app.services.availability import (
    enrich_schedule,
    enrich_schedules,
    get_booked_slots
)

from app.services.guide_availability import (
    validate_schedule_guides
)


router = APIRouter(prefix="/api/departures", tags=["Tour Schedules"])



# Lấy danh sách lịch khởi hành đang mở
@router.get("/", response_model=list[TourScheduleResponse])
def get_departures(
    db: Session = Depends(get_db)
):
    schedules = (
        db.query(TourSchedule)
        .join(Tour, Tour.id == TourSchedule.tour_id)
        .filter(
            TourSchedule.status == "open",
            Tour.status == "active",
            TourSchedule.departure_date >= date.today()
        )
        .order_by(TourSchedule.departure_date.asc())
        .all()
    )

    return enrich_schedules(db, schedules)




# ADMIN xem toàn bộ lịch khởi hành
@router.get(
    "/admin/all",
    response_model=list[TourScheduleResponse]
)
def get_all_departures(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    schedules = (
        db.query(TourSchedule)
        .order_by(TourSchedule.id.desc())
        .all()
    )

    return enrich_schedules(db, schedules)



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

    return enrich_schedule(db, schedule)


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

    return enrich_schedule(db, schedule)



# ADMIN cập nhật lịch khởi hành
@router.put(
    "/{schedule_id}",
    response_model=TourScheduleResponse
)
def update_departure(
    schedule_id: int,
    data: TourScheduleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # 1. Khóa bản ghi lịch khởi hành
    schedule = (
        db.query(TourSchedule)
        .filter(TourSchedule.id == schedule_id)
        .with_for_update()
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành"
        )

    # 2. Không sửa lịch đã hủy
    if schedule.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Không thể cập nhật lịch đã hủy"
        )

    # 3. Kiểm tra Tour
    tour = db.get(Tour, data.tour_id)

    if not tour or tour.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Tour không tồn tại hoặc đã ngừng kinh doanh"
        )

    # 4. Kiểm tra ngày khởi hành
    if (
        data.status == "open"
        and data.departure_date < date.today()
    ):
        raise HTTPException(
            status_code=422,
            detail="Không thể mở lịch khởi hành trong quá khứ"
        )

    # 5. Tính số chỗ đang được giữ
    booked = get_booked_slots(
        db,
        schedule.id,
        lock=True
    )

    # 6. Kiểm tra sức chứa mới
    if data.capacity < booked:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Sức chứa không được nhỏ hơn "
                f"số khách đã đặt ({booked} khách)"
            )
        )

    # 7. Không đổi Tour nếu đã có đơn
    if data.tour_id != schedule.tour_id:
        existing_booking = (
            db.query(Booking.id)
            .filter(
                Booking.schedule_id == schedule.id
            )
            .with_for_update()
            .first()
        )

        if existing_booking:
            raise HTTPException(
                status_code=409,
                detail="Không thể thay đổi Tour của lịch đã có đơn đặt"
            )

    # 8. Kiểm tra thay đổi ngày
    dates_changed = (
        data.departure_date != schedule.departure_date
        or data.return_date != schedule.return_date
    )

    if dates_changed and booked > 0:
        raise HTTPException(
            status_code=409,
            detail="Không thể thay đổi ngày khi lịch đang có khách đặt"
        )

    # 9. Không hủy lịch đang giữ chỗ
    if data.status == "cancelled" and booked > 0:
        raise HTTPException(
            status_code=409,
            detail="Không thể hủy lịch đang có khách đặt"
        )
        
    # 10. Kiểm tra xung đột lịch hướng dẫn viên
    if dates_changed and data.status != "cancelled":
        validate_schedule_guides(
            db=db,
            schedule_id=schedule.id,
            departure_date=data.departure_date,
            return_date=data.return_date
        )

    # 11. Cập nhật dữ liệu
    for field, value in data.model_dump().items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return enrich_schedule(db, schedule)




# ADMIN hủy lịch khởi hành
@router.delete("/{schedule_id}")
def cancel_departure(
    schedule_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # 1. Khóa bản ghi lịch
    schedule = (
        db.query(TourSchedule)
        .filter(TourSchedule.id == schedule_id)
        .with_for_update()
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành"
        )

    # 2. Kiểm tra trạng thái hiện tại
    if schedule.status == "cancelled":
        raise HTTPException(
            status_code=409,
            detail="Lịch khởi hành đã bị hủy trước đó"
        )

    # 3. Kiểm tra số khách đã đặt
    booked = get_booked_slots(
        db,
        schedule.id,
        lock=True
    )

    if booked > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Không thể hủy lịch vì đang có "
                f"{booked} khách đặt Tour"
            )
        )

    # 4. Hủy lịch
    schedule.status = "cancelled"

    db.commit()

    return {
        "message": "Đã hủy lịch khởi hành thành công"
    }
