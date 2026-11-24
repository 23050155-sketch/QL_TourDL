
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.tour import Tour
from app.models.tour_schedule import TourSchedule
from app.schemas.tour_schedule import TourScheduleResponse


# Các trạng thái đơn được tính vào sức chứa
OCCUPIED_STATUSES = (
    "pending",
    "awaiting_payment",
    "paid",
    "completed",
)


# Tính số chỗ đã đặt của một lịch
def get_booked_slots(
    db: Session,
    schedule_id: int,
    lock: bool = False
) -> int:

    # Dùng khi tạo đơn hoặc cập nhật sức chứa
    if lock:
        rows = (
            db.query(Booking.number_of_people)
            .filter(
                Booking.schedule_id == schedule_id,
                Booking.status.in_(OCCUPIED_STATUSES)
            )
            .with_for_update()
            .all()
        )

        return sum(row[0] for row in rows)

    # Dùng khi chỉ đọc thông tin
    booked = (
        db.query(
            func.coalesce(
                func.sum(Booking.number_of_people),
                0
            )
        )
        .filter(
            Booking.schedule_id == schedule_id,
            Booking.status.in_(OCCUPIED_STATUSES)
        )
        .scalar()
    )

    return int(booked)


# Bổ sung thông tin sức chứa cho nhiều lịch
def enrich_schedules(
    db: Session,
    schedules: list[TourSchedule]
) -> list[TourScheduleResponse]:

    if not schedules:
        return []

    schedule_ids = [s.id for s in schedules]
    tour_ids = {s.tour_id for s in schedules}

    # Tính tổng số khách theo từng lịch
    booked_rows = (
        db.query(
            Booking.schedule_id,
            func.sum(Booking.number_of_people)
        )
        .filter(
            Booking.schedule_id.in_(schedule_ids),
            Booking.status.in_(OCCUPIED_STATUSES)
        )
        .group_by(Booking.schedule_id)
        .all()
    )

    booked_map = {
        schedule_id: int(total)
        for schedule_id, total in booked_rows
    }

    # Lấy trạng thái các Tour liên quan
    tour_rows = (
        db.query(Tour.id, Tour.status)
        .filter(Tour.id.in_(tour_ids))
        .all()
    )

    tour_status_map = dict(tour_rows)

    results = []
    today = date.today()

    for schedule in schedules:
        booked = booked_map.get(schedule.id, 0)

        remaining = max(
            0,
            schedule.capacity - booked
        )

        is_full = remaining == 0

        is_bookable = (
            schedule.status == "open"
            and schedule.departure_date >= today
            and tour_status_map.get(
                schedule.tour_id
            ) == "active"
            and remaining > 0
        )

        results.append(
            TourScheduleResponse(
                id=schedule.id,
                tour_id=schedule.tour_id,
                departure_date=schedule.departure_date,
                return_date=schedule.return_date,
                capacity=schedule.capacity,
                status=schedule.status,
                booked_slots=booked,
                remaining_slots=remaining,
                is_full=is_full,
                is_bookable=is_bookable
            )
        )

    return results


# Bổ sung thông tin sức chứa cho một lịch
def enrich_schedule(
    db: Session,
    schedule: TourSchedule
) -> TourScheduleResponse:

    return enrich_schedules(db, [schedule])[0]
