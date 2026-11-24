
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.guide import TourGuide, GuideAssignment
from app.models.tour_schedule import TourSchedule
from app.models.user import User
from app.routers.auth import require_admin
from app.schemas.guide import (
    GuideAssignmentCreate,
    GuideAssignmentResponse,
)

from app.services.guide_availability import (
    lock_guide,
    check_guide_conflict
)


router = APIRouter(
    prefix="/api/guide-assignments",
    tags=["Guide Assignments"],
)


# 1. ADMIN xem danh sách phân công
@router.get(
    "/",
    response_model=list[GuideAssignmentResponse],
)
def get_guide_assignments(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(GuideAssignment)
        .order_by(GuideAssignment.id.desc())
        .all()
    )



# 2. ADMIN phân công hướng dẫn viên
@router.post(
    "/",
    response_model=GuideAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_guide_assignment(
    data: GuideAssignmentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # 1. Khóa lịch khởi hành
    schedule = (
        db.query(TourSchedule)
        .filter(
            TourSchedule.id == data.schedule_id
        )
        .populate_existing()
        .with_for_update()
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy lịch khởi hành"
        )

    if schedule.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Không thể phân công cho lịch đã hủy"
        )

    # 2. Khóa hướng dẫn viên
    guide = lock_guide(db, data.guide_id)

    if not guide:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy hướng dẫn viên"
        )

    if guide.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Hướng dẫn viên không hoạt động"
        )

    # 3. Kiểm tra phân công trùng
    existing = (
        db.query(GuideAssignment.id)
        .filter(
            GuideAssignment.schedule_id == data.schedule_id,
            GuideAssignment.guide_id == data.guide_id
        )
        .with_for_update()
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail=(
                "Hướng dẫn viên đã được "
                "phân công cho lịch này"
            )
        )

    # 4. Kiểm tra trùng thời gian
    check_guide_conflict(
        db=db,
        guide_id=guide.id,
        schedule_id=schedule.id,
        departure_date=schedule.departure_date,
        return_date=schedule.return_date
    )

    # 5. Tạo phân công
    assignment = GuideAssignment(
        schedule_id=schedule.id,
        guide_id=guide.id
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment



# 3. ADMIN hủy phân công
@router.delete("/{assignment_id}")
def delete_guide_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    assignment = db.get(GuideAssignment, assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy phân công",
        )

    db.delete(assignment)
    db.commit()

    return {
        "message": "Hủy phân công hướng dẫn viên thành công",
        "id": assignment_id,
    }
