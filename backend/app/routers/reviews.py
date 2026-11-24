
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review
from app.models.user import User
from app.models.tour import Tour
from app.models.booking import Booking
from app.models.tour_schedule import TourSchedule

from app.routers.auth import (
    get_current_user,
    require_admin,
)

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewSummary,
)


router = APIRouter(
    prefix="/api/reviews",
    tags=["Reviews"],
)


# Kiểm tra quyền CUSTOMER
def require_customer(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "customer":
        raise HTTPException(
            status_code=403,
            detail="Chỉ khách hàng mới được thực hiện chức năng này",
        )

    return current_user


# 1. Xem danh sách đánh giá của Tour
@router.get(
    "/tour/{tour_id}",
    response_model=list[ReviewResponse],
)
def get_tour_reviews(
    tour_id: int,
    db: Session = Depends(get_db),
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour",
        )

    return (
        db.query(Review)
        .filter(Review.tour_id == tour_id)
        .order_by(Review.id.desc())
        .all()
    )


# 2. Thống kê đánh giá của Tour
@router.get(
    "/tour/{tour_id}/summary",
    response_model=ReviewSummary,
)
def get_review_summary(
    tour_id: int,
    db: Session = Depends(get_db),
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour",
        )

    rows = (
        db.query(
            Review.rating,
            func.count(Review.id),
        )
        .filter(Review.tour_id == tour_id)
        .group_by(Review.rating)
        .all()
    )

    counts = {
        rating: count
        for rating, count in rows
    }

    total = sum(counts.values())

    average = (
        sum(
            rating * count
            for rating, count in counts.items()
        ) / total
        if total > 0
        else 0
    )

    return {
        "tour_id": tour_id,
        "average_rating": round(average, 2),
        "total_reviews": total,
        "five_stars": counts.get(5, 0),
        "four_stars": counts.get(4, 0),
        "three_stars": counts.get(3, 0),
        "two_stars": counts.get(2, 0),
        "one_star": counts.get(1, 0),
    }


# 3. CUSTOMER xem đánh giá của mình
@router.get(
    "/my",
    response_model=list[ReviewResponse],
)
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.id.desc())
        .all()
    )


# 4. ADMIN xem toàn bộ đánh giá
@router.get(
    "/admin",
    response_model=list[ReviewResponse],
)
def get_all_reviews(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(Review)
        .order_by(Review.id.desc())
        .all()
    )


# 5. CUSTOMER tạo đánh giá
@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    tour = db.get(Tour, data.tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour",
        )

    # Kiểm tra khách hàng đã hoàn thành Tour chưa
    completed_booking = (
        db.query(Booking)
        .join(
            TourSchedule,
            Booking.schedule_id == TourSchedule.id,
        )
        .filter(
            Booking.user_id == current_user.id,
            TourSchedule.tour_id == data.tour_id,
            Booking.status == "completed",
        )
        .first()
    )

    if not completed_booking:
        raise HTTPException(
            status_code=403,
            detail="Bạn phải hoàn thành chuyến đi trước khi đánh giá",
        )

    # Kiểm tra khách hàng đã đánh giá Tour chưa
    existing = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.tour_id == data.tour_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Bạn đã đánh giá Tour này",
        )

    review = Review(
        user_id=current_user.id,
        tour_id=data.tour_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Không thể tạo đánh giá do ràng buộc dữ liệu",
        )

    db.refresh(review)

    return review


# 6. CUSTOMER cập nhật đánh giá của mình
@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    review = db.get(Review, review_id)

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đánh giá",
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền sửa đánh giá này",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "rating" in update_data and update_data["rating"] is None:
        raise HTTPException(
            status_code=422,
            detail="Điểm đánh giá không được để trống",
        )

    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)

    return review


# 7. Xóa đánh giá
@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.get(Review, review_id)

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đánh giá",
        )

    if (
        current_user.role != "admin"
        and review.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xóa đánh giá này",
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Xóa đánh giá thành công",
        "id": review_id,
    }
