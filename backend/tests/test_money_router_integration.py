
import unittest

from app.models.booking import Booking
from app.models.payment import Payment

from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from app.routers.bookings import create_booking

from app.routers.payments import (
    create_payment,
    admin_confirm_payment,
)

from app.schemas.booking import BookingCreate

from app.schemas.payment import (
    PaymentCreate,
    PaymentConfirm,
)


D = Decimal


class TestMoneyRouterIntegration(
    unittest.TestCase
):

    def setUp(self):
        self.db = MagicMock()

        self.customer = SimpleNamespace(
            id=1,
            role="customer",
            status="active",
        )

        self.admin = SimpleNamespace(
            id=2,
            role="admin",
            status="active",
        )

    def assert_rejected(
        self,
        callback,
        expected_detail,
    ):
        with self.assertRaises(
            HTTPException
        ) as context:
            callback()

        self.assertEqual(
            context.exception.status_code,
            409,
        )

        self.assertEqual(
            context.exception.detail,
            expected_detail,
        )

        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        self.db.rollback.assert_called_once()

    @patch(
        "app.routers.bookings.get_booked_slots",
        return_value=0,
    )
    def test_booking_total_overflow(
        self,
        mock_booked_slots,
    ):
        schedule = SimpleNamespace(
            id=1,
            tour_id=1,
            capacity=10,
            status="open",
            departure_date=(
                date.today()
                + timedelta(days=10)
            ),
        )

        tour = SimpleNamespace(
            id=1,
            status="active",
            base_price=D("6000000000"),
        )

        self.db.query.return_value \
            .filter.return_value \
            .with_for_update.return_value \
            .first.return_value = schedule

        self.db.get.return_value = tour

        data = BookingCreate(
            schedule_id=1,
            number_of_people=2,
            passengers=[
                {"full_name": "Test Passenger A"},
                {"full_name": "Test Passenger B"},
            ],
        )

        self.assert_rejected(
            lambda: create_booking(
                data=data,
                db=self.db,
                current_user=self.customer,
            ),
            expected_detail=(
                "Đơn giá hoặc tổng tiền đặt Tour "
                "không nằm trong giới hạn cho phép"
            ),
        )

        mock_booked_slots.assert_called_once()

        mock_booked_slots.assert_called()

    
    def test_payment_invalid_booking_amount(self):

        booking = SimpleNamespace(
            id=1,
            user_id=1,
            status="awaiting_payment",
            unit_price=D("100"),
            number_of_people=3,
            total_amount=D("200"),
        )

        # Mock truy vấn Booking
        booking_query = MagicMock()

        booking_query.filter.return_value \
            .with_for_update.return_value \
            .first.return_value = booking

        # Mock truy vấn kiểm tra Payment trùng
        payment_query = MagicMock()

        payment_query.filter.return_value \
            .populate_existing.return_value \
            .with_for_update.return_value \
            .first.return_value = None

        # Phân biệt từng Model được truy vấn
        self.db.query.side_effect = {
            Booking: booking_query,
            Payment: payment_query,
        }.__getitem__

        data = PaymentCreate(
            booking_id=1,
            payment_method="cash",
        )

        self.assert_rejected(
            lambda: create_payment(
                data=data,
                db=self.db,
                current_user=self.customer,
            ),
            expected_detail=(
                "Số tiền của đơn đặt Tour "
                "không hợp lệ hoặc không nhất quán"
            ),
        )

        self.assertEqual(
            booking.status,
            "awaiting_payment",
        )


    
    def check_confirmation(
        self,
        booking_total,
        payment_amount,
        expected_detail,
    ):
        booking = SimpleNamespace(
            id=1,
            user_id=1,
            status="awaiting_payment",
            unit_price=D("100"),
            number_of_people=3,
            total_amount=booking_total,
        )

        payment = SimpleNamespace(
            id=1,
            booking_id=1,
            status="pending",
            amount=payment_amount,
            transaction_code=None,
            paid_at=None,
        )

        # 1. Mock truy vấn lấy Booking ID
        reference_query = MagicMock()

        reference_query.filter.return_value \
            .first.return_value = (booking.id,)

        # 2. Mock truy vấn khóa Booking
        booking_query = MagicMock()

        booking_query.filter.return_value \
            .populate_existing.return_value \
            .with_for_update.return_value \
            .first.return_value = booking

        # 3. Mock truy vấn khóa Payment
        payment_query = MagicMock()

        payment_query.filter.return_value \
            .populate_existing.return_value \
            .with_for_update.return_value \
            .first.return_value = payment

        # Ghi nhận thứ tự thực hiện truy vấn
        query_order = []

        def mock_query(model):

            if model is Payment.booking_id:
                query_order.append("payment_reference")
                return reference_query

            if model is Booking:
                query_order.append("booking")
                return booking_query

            if model is Payment:
                query_order.append("payment")
                return payment_query

            raise AssertionError(
                "Unexpected database query"
            )

        self.db.query.side_effect = mock_query

        self.assert_rejected(
            lambda: admin_confirm_payment(
                payment_id=1,
                data=PaymentConfirm(),
                db=self.db,
                admin=self.admin,
            ),
            expected_detail=expected_detail,
        )

        # Kiểm tra thứ tự truy vấn
        self.assertEqual(
            query_order,
            [
                "payment_reference",
                "booking",
                "payment",
            ],
        )

        # Kiểm tra trạng thái không bị thay đổi
        self.assertEqual(
            booking.status,
            "awaiting_payment",
        )

        self.assertEqual(
            payment.status,
            "pending",
        )

        self.assertIsNone(payment.paid_at)
        self.assertIsNone(payment.transaction_code)


    def test_confirm_amount_mismatch(self):
        self.check_confirmation(
            D("300"),
            D("299.99"),
            expected_detail=(
                "Số tiền thanh toán không khớp "
                "với đơn đặt Tour"
            ),
        )


    def test_confirm_invalid_booking_total(self):
        self.check_confirmation(
            D("200"),
            D("200"),
            expected_detail=(
                "Dữ liệu số tiền thanh toán "
                "không hợp lệ"
            ),
        )


    def test_confirm_negative_payment(self):
        self.check_confirmation(
            D("300"),
            D("-300"),
            expected_detail=(
                "Dữ liệu số tiền thanh toán "
                "không hợp lệ"
            ),
        )


if __name__ == "__main__":
    unittest.main()
