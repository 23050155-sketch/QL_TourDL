
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User

from app.routers.auth import (
    require_customer,
    require_admin
)

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentConfirm,
)


from app.core.money_validation import (
    validate_money_amount,
    validate_booking_amount,
)


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
)



# 1. Khách hàng tạo yêu cầu thanh toán
@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=201,
)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        # Kiểm tra quyền sở hữu và khóa Booking
        booking = (
            db.query(Booking)
            .filter(
                Booking.id == data.booking_id,
                Booking.user_id == current_user.id,
            )
            .with_for_update()
            .first()
        )

        # Không tìm thấy hoặc không thuộc sở hữu
        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy đơn đặt Tour",
            )

        # Kiểm tra trạng thái đơn đặt Tour
        if booking.status != "awaiting_payment":
            raise HTTPException(
                status_code=409,
                detail="Đơn chưa được duyệt hoặc đã thanh toán",
            )

        # Kiểm tra yêu cầu thanh toán đã tồn tại
        existing_payment = (
            db.query(Payment)
            .filter(
                Payment.booking_id == booking.id,
                Payment.status.in_(["pending", "success"]),
            )
            .populate_existing()
            .with_for_update()
            .first()
        )

        if existing_payment:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Đơn đã có yêu cầu thanh toán "
                    "đang chờ hoặc đã thành công"
                ),
            )

        
        # Kiểm tra tính hợp lệ của số tiền Booking
        try:
            amount = validate_booking_amount(
                unit_price=booking.unit_price,
                number_of_people=booking.number_of_people,
                total_amount=booking.total_amount,
            )

        except ValueError:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Số tiền của đơn đặt Tour "
                    "không hợp lệ hoặc không nhất quán"
                ),
            ) from None

        # Tạo yêu cầu thanh toán
        payment = Payment(
            booking_id=booking.id,
            amount=amount,
            payment_method=data.payment_method,
            status="pending",
        )


        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise



# 2. Khách hàng xem lịch sử thanh toán của mình
@router.get(
    "/my",
    response_model=list[PaymentResponse],
)
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    return (
        db.query(Payment)
        .join(Booking, Payment.booking_id == Booking.id)
        .filter(Booking.user_id == current_user.id)
        .order_by(Payment.id.desc())
        .all()
    )


# 3. ADMIN xem tất cả thanh toán
@router.get(
    "/admin/all",
    response_model=list[PaymentResponse],
)
def admin_get_all_payments(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return (
        db.query(Payment)
        .order_by(Payment.id.desc())
        .all()
    )



# 4. ADMIN xác nhận đã nhận tiền
@router.patch(
    "/admin/{payment_id}/confirm",
    response_model=PaymentResponse,
)
def admin_confirm_payment(
    payment_id: int,
    data: PaymentConfirm,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    try:
        # 1. Xác định Booking ID, chưa khóa Payment
        payment_ref = (
            db.query(Payment.booking_id)
            .filter(Payment.id == payment_id)
            .first()
        )

        if not payment_ref:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy thanh toán",
            )

        booking_id = payment_ref[0]

        # 2. Khóa Booking trước
        booking = (
            db.query(Booking)
            .filter(Booking.id == booking_id)
            .populate_existing()
            .with_for_update()
            .first()
        )

        if not booking:
            raise HTTPException(
                status_code=409,
                detail="Đơn đặt Tour không còn tồn tại",
            )

        # 3. Khóa Payment sau
        payment = (
            db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.booking_id == booking.id,
            )
            .populate_existing()
            .with_for_update()
            .first()
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy thanh toán",
            )

        # 4. Kiểm tra lại trạng thái sau khi khóa
        if payment.status != "pending":
            raise HTTPException(
                status_code=409,
                detail="Thanh toán đã được xử lý",
            )

        if booking.status != "awaiting_payment":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Đơn đặt Tour không ở trạng thái "
                    "chờ thanh toán"
                ),
            )

        # 5. Kiểm tra tính hợp lệ của số tiền
        try:
            booking_amount = validate_booking_amount(
                unit_price=booking.unit_price,
                number_of_people=booking.number_of_people,
                total_amount=booking.total_amount,
            )

            payment_amount = validate_money_amount(
                payment.amount
            )

        except ValueError:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Dữ liệu số tiền thanh toán "
                    "không hợp lệ"
                ),
            ) from None

        # 6. Kiểm tra số tiền thanh toán
        if payment_amount != booking_amount:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Số tiền thanh toán không khớp "
                    "với đơn đặt Tour"
                ),
            )

        # 7. Cập nhật thông tin giao dịch
        if data.transaction_code:
            payment.transaction_code = data.transaction_code

        payment.status = "success"

        payment.paid_at = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)

        booking.status = "paid"

        # 8. Lưu đồng thời Booking và Payment
        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise

