
import unittest

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

    def assert_rejected(self, callback):
        with self.assertRaises(
            HTTPException
        ) as context:
            callback()

        self.assertEqual(
            context.exception.status_code,
            409,
        )

        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        self.db.rollback.assert_called()

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
            )
        )

        mock_booked_slots.assert_called()

    def test_payment_invalid_booking_amount(
        self,
    ):
        booking = SimpleNamespace(
            id=1,
            user_id=1,
            status="awaiting_payment",
            unit_price=D("100"),
            number_of_people=3,
            total_amount=D("200"),
        )

        query = self.db.query.return_value

        query.filter.return_value \
            .with_for_update.return_value \
            .first.return_value = booking

        query.filter.return_value \
            .first.return_value = None

        data = PaymentCreate(
            booking_id=1,
            payment_method="cash",
        )

        self.assert_rejected(
            lambda: create_payment(
                data=data,
                db=self.db,
                current_user=self.customer,
            )
        )

    def check_confirmation(
        self,
        booking_total,
        payment_amount,
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

        self.db.query.return_value \
            .filter.return_value \
            .with_for_update.return_value \
            .first.side_effect = [
                payment,
                booking,
            ]

        self.assert_rejected(
            lambda: admin_confirm_payment(
                payment_id=1,
                data=PaymentConfirm(),
                db=self.db,
                admin=self.admin,
            )
        )

        self.assertEqual(
            booking.status,
            "awaiting_payment",
        )

        self.assertEqual(
            payment.status,
            "pending",
        )

        self.assertIsNone(payment.paid_at)

    def test_confirm_amount_mismatch(self):
        self.check_confirmation(
            D("300"),
            D("299.99"),
        )

    def test_confirm_invalid_booking_total(self):
        self.check_confirmation(
            D("200"),
            D("200"),
        )

    def test_confirm_negative_payment(self):
        self.check_confirmation(
            D("300"),
            D("-300"),
        )


if __name__ == "__main__":
    unittest.main()
