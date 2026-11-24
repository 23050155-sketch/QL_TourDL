
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.booking import Booking, BookingPassenger
from app.models.tour import Tour
from app.models.tour_schedule import TourSchedule
from app.models.user import User

from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
)

from app.routers.auth import (
    require_admin,
    require_customer
)

from app.models.guide import (
    TourGuide,
    GuideAssignment,
)

from app.schemas.guide import GuideContactResponse

from app.services.availability import get_booked_slots



router = APIRouter(prefix="/api/bookings", tags=["Bookings"])



# Tạo đơn đặt Tour và kiểm tra sức chứa trong transaction
@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    if len(data.passengers) != data.number_of_people:
        raise HTTPException(
            status_code=422,
            detail="Số hành khách phải bằng number_of_people",
        )

    try:
        # Khóa lịch để tránh hai yêu cầu cùng đặt vượt số chỗ
        schedule = (
            db.query(TourSchedule)
            .filter(TourSchedule.id == data.schedule_id)
            .with_for_update()
            .first()
        )

        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lịch khởi hành",
            )

        if schedule.status != "open":
            raise HTTPException(
                status_code=409,
                detail="Lịch khởi hành không còn mở",
            )

        if schedule.departure_date < date.today():
            raise HTTPException(
                status_code=409,
                detail="Lịch khởi hành đã qua",
            )

        tour = db.get(Tour, schedule.tour_id)

        if not tour or tour.status != "active":
            raise HTTPException(
                status_code=409,
                detail="Tour không còn hoạt động",
            )

        booked = get_booked_slots(
            db,
            schedule.id,
            lock=True
        )

        remaining = max(
            0,
            schedule.capacity - booked
        )

        if data.number_of_people > remaining:
            raise HTTPException(
                status_code=409,
                detail=f"Không đủ chỗ. Hiện còn {remaining} chỗ",
            )

        unit_price = Decimal(str(tour.base_price))
        total_amount = unit_price * data.number_of_people

        booking = Booking(
            user_id=current_user.id,
            schedule_id=schedule.id,
            number_of_people=data.number_of_people,
            unit_price=unit_price,
            total_amount=total_amount,
            status="pending",
        )

        for passenger in data.passengers:
            booking.passengers.append(
                BookingPassenger(**passenger.model_dump())
            )

        db.add(booking)
        db.commit()

        booking_id = booking.id

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .one()
    )


# Khách hàng xem các đơn đặt Tour của mình
@router.get(
    "/my",
    response_model=list[BookingListResponse]
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.id.desc())
        .all()
    )



# ADMIN xem tất cả đơn đặt Tour
@router.get(
    "/admin/all",
    response_model=list[BookingListResponse]
)
def admin_get_all_bookings(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(Booking)
        .order_by(Booking.id.desc())
        .all()
    )


# ADMIN xem chi tiết một đơn đặt Tour
@router.get(
    "/admin/{booking_id}",
    response_model=BookingResponse,
)
def admin_get_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    booking = (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn đặt Tour",
        )

    return booking


# ADMIN duyệt đơn đặt Tour
@router.patch(
    "/admin/{booking_id}/approve",
    response_model=BookingResponse,
)
def admin_approve_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        booking = (
            db.query(Booking)
            .filter(Booking.id == booking_id)
            .with_for_update()
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đơn đặt Tour",
            )

        if booking.status != "pending":
            raise HTTPException(
                status_code=409,
                detail="Chỉ có thể duyệt đơn đang chờ xử lý",
            )

        schedule = db.get(TourSchedule, booking.schedule_id)

        if not schedule or schedule.status != "open":
            raise HTTPException(
                status_code=409,
                detail="Lịch khởi hành không còn mở",
            )

        booking.status = "awaiting_payment"
        db.commit()

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .one()
    )


# ADMIN từ chối đơn đặt Tour
@router.patch(
    "/admin/{booking_id}/reject",
    response_model=BookingResponse,
)
def admin_reject_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        booking = (
            db.query(Booking)
            .filter(Booking.id == booking_id)
            .with_for_update()
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đơn đặt Tour",
            )

        if booking.status != "pending":
            raise HTTPException(
                status_code=409,
                detail="Chỉ có thể từ chối đơn đang chờ xử lý",
            )

        booking.status = "rejected"
        db.commit()

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .one()
    )
    


# Khách hàng xem chi tiết đơn đặt Tour của mình
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    booking = (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn đặt Tour",
        )

    return booking





# Khách hàng hủy đơn đặt Tour
@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_my_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        booking = (
            db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đơn đặt Tour của bạn",
            )

        if booking.status not in (
            "pending",
            "awaiting_payment",
        ):
            raise HTTPException(
                status_code=409,
                detail="Trạng thái đơn không cho phép hủy",
            )

        schedule = db.get(
            TourSchedule,
            booking.schedule_id,
        )

        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lịch khởi hành",
            )

        if schedule.departure_date <= date.today():
            raise HTTPException(
                status_code=409,
                detail="Không thể hủy khi đã đến ngày khởi hành",
            )

        # Hủy các yêu cầu thanh toán chưa xử lý
        from app.models.payment import Payment

        pending_payments = (
            db.query(Payment)
            .filter(
                Payment.booking_id == booking.id,
                Payment.status == "pending",
            )
            .with_for_update()
            .all()
        )

        for payment in pending_payments:
            payment.status = "failed"

        booking.status = "cancelled"

        db.commit()

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .one()
    )





# ADMIN đánh dấu đơn đã hoàn thành chuyến đi
@router.patch(
    "/admin/{booking_id}/complete",
    response_model=BookingResponse,
)
def admin_complete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        booking = (
            db.query(Booking)
            .filter(Booking.id == booking_id)
            .with_for_update()
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đơn đặt Tour",
            )

        if booking.status != "paid":
            raise HTTPException(
                status_code=409,
                detail="Chỉ có thể hoàn thành đơn đã thanh toán",
            )

        schedule = db.get(
            TourSchedule,
            booking.schedule_id,
        )

        if not schedule:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy lịch khởi hành",
            )

        if schedule.return_date > date.today():
            raise HTTPException(
                status_code=409,
                detail="Chuyến đi chưa kết thúc",
            )

        booking.status = "completed"
        db.commit()

    except Exception:
        db.rollback()
        raise

    return (
        db.query(Booking)
        .options(selectinload(Booking.passengers))
        .filter(Booking.id == booking_id)
        .one()
    )
    
    


# CUSTOMER xem thông tin HDV của Booking đã thanh toán
@router.get(
    "/{booking_id}/guides",
    response_model=list[GuideContactResponse],
)
def get_booking_guides(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    # 1. Kiểm tra quyền sở hữu Booking
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn đặt Tour",
        )

    # 2. Kiểm tra trạng thái thanh toán
    if booking.status != "paid":
        raise HTTPException(
            status_code=403,
            detail=(
                "Chỉ được xem thông tin liên hệ "
                "hướng dẫn viên khi đơn đã thanh toán "
                "và chưa hoàn thành"
            ),
        )

    # 3. Lấy hướng dẫn viên được phân công
    guides = (
        db.query(TourGuide)
        .join(
            GuideAssignment,
            GuideAssignment.guide_id == TourGuide.id,
        )
        .filter(
            GuideAssignment.schedule_id
            == booking.schedule_id,
            TourGuide.status == "active",
        )
        .order_by(TourGuide.id.asc())
        .all()
    )

    # 4. Trả về thông tin liên hệ
    return guides

