
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.guide import TourGuide, GuideAssignment
from app.models.tour_schedule import TourSchedule


# Khóa bản ghi hướng dẫn viên
def lock_guide(
    db: Session,
    guide_id: int
):
    return (
        db.query(TourGuide)
        .filter(TourGuide.id == guide_id)
        .populate_existing()
        .with_for_update()
        .first()
    )


# Kiểm tra hướng dẫn viên có bị trùng lịch không
def check_guide_conflict(
    db: Session,
    guide_id: int,
    schedule_id: int,
    departure_date: date,
    return_date: date
):
    overlapping = (
        db.query(TourSchedule.id)
        .join(
            GuideAssignment,
            GuideAssignment.schedule_id == TourSchedule.id
        )
        .filter(
            GuideAssignment.guide_id == guide_id,
            TourSchedule.id != schedule_id,
            TourSchedule.status != "cancelled",
            TourSchedule.departure_date <= return_date,
            TourSchedule.return_date >= departure_date
        )
        .with_for_update()
        .first()
    )

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Hướng dẫn viên ID {guide_id} "
                f"bị trùng với lịch khởi hành "
                f"ID {overlapping[0]}"
            )
        )


# Kiểm tra toàn bộ hướng dẫn viên của một lịch
def validate_schedule_guides(
    db: Session,
    schedule_id: int,
    departure_date: date,
    return_date: date
):
    assignments = (
        db.query(GuideAssignment.guide_id)
        .filter(
            GuideAssignment.schedule_id == schedule_id
        )
        .with_for_update()
        .all()
    )

    guide_ids = sorted({
        row[0] for row in assignments
    })

    # Khóa hướng dẫn viên theo thứ tự ID
    for guide_id in guide_ids:
        guide = lock_guide(db, guide_id)

        if not guide:
            raise HTTPException(
                status_code=409,
                detail="Hướng dẫn viên không còn tồn tại"
            )

    # Kiểm tra xung đột thời gian
    for guide_id in guide_ids:
        check_guide_conflict(
            db=db,
            guide_id=guide_id,
            schedule_id=schedule_id,
            departure_date=departure_date,
            return_date=return_date
        )
