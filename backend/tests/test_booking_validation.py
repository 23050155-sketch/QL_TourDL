
import unittest

from datetime import date, timedelta

from pydantic import ValidationError

from app.schemas.booking import (
    BookingCreate,
    PassengerCreate,
    PassengerResponse,
)

from app.core.validation import (
    MAX_BOOKING_PEOPLE,
    MAX_UNSIGNED_BIGINT,
)


class TestBookingValidation(unittest.TestCase):

    def valid_booking(self):
        return {
            "schedule_id": 1,
            "number_of_people": 1,
            "passengers": [
                {
                    "full_name": "Nguyen Van Test",
                    "date_of_birth": "2000-01-01",
                    "phone": "0900000000",
                }
            ],
        }

    # 1. Booking hợp lệ
    def test_valid_booking(self):
        booking = BookingCreate(**self.valid_booking())

        self.assertEqual(booking.number_of_people, 1)
        self.assertEqual(len(booking.passengers), 1)

    # 2. ID bằng 0
    def test_zero_schedule_id(self):
        data = self.valid_booking()
        data["schedule_id"] = 0

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 3. ID vượt giới hạn MySQL
    def test_schedule_id_overflow(self):
        data = self.valid_booking()
        data["schedule_id"] = MAX_UNSIGNED_BIGINT + 1

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 4. ID dạng chuỗi
    def test_string_schedule_id(self):
        data = self.valid_booking()
        data["schedule_id"] = "1"

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 5. Số lượng khách bằng 0
    def test_zero_people(self):
        data = self.valid_booking()
        data["number_of_people"] = 0

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 6. Số lượng khách vượt giới hạn
    def test_too_many_people(self):
        data = self.valid_booking()
        data["number_of_people"] = MAX_BOOKING_PEOPLE + 1

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 7. Số lượng khách dạng boolean
    def test_boolean_people(self):
        data = self.valid_booking()
        data["number_of_people"] = True

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 8. Danh sách hành khách trống
    def test_empty_passengers(self):
        data = self.valid_booking()
        data["passengers"] = []

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 9. Số lượng hành khách không khớp
    def test_passenger_count_mismatch(self):
        data = self.valid_booking()
        data["number_of_people"] = 2

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 10. Danh sách hành khách vượt giới hạn
    def test_too_many_passengers(self):
        data = self.valid_booking()
        data["number_of_people"] = MAX_BOOKING_PEOPLE

        passenger = data["passengers"][0]

        data["passengers"] = [
            passenger.copy()
            for _ in range(MAX_BOOKING_PEOPLE + 1)
        ]

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 11. Ngày sinh trong tương lai
    def test_future_birth_date(self):
        tomorrow = date.today() + timedelta(days=1)

        with self.assertRaises(ValidationError):
            PassengerCreate(
                full_name="Nguyen Van Test",
                date_of_birth=tomorrow,
            )

    # 12. Không cung cấp ngày sinh
    def test_optional_birth_date(self):
        passenger = PassengerCreate(
            full_name="Nguyen Van Test"
        )

        self.assertIsNone(passenger.date_of_birth)

    # 13. Trường dư thừa trong Booking
    def test_extra_booking_field(self):
        data = self.valid_booking()
        data["total_amount"] = 1000

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 14. Trường dư thừa trong hành khách
    def test_extra_passenger_field(self):
        data = self.valid_booking()
        data["passengers"][0]["booking_id"] = 1

        with self.assertRaises(ValidationError):
            BookingCreate(**data)

    # 15. Kiểm tra giới hạn hợp lệ
    def test_valid_max_people(self):
        data = self.valid_booking()

        data["number_of_people"] = MAX_BOOKING_PEOPLE

        passenger = data["passengers"][0]

        data["passengers"] = [
            passenger.copy()
            for _ in range(MAX_BOOKING_PEOPLE)
        ]

        booking = BookingCreate(**data)

        self.assertEqual(
            len(booking.passengers),
            MAX_BOOKING_PEOPLE
        )

    # 16. Response không áp dụng Validator ngày sinh mới
    def test_passenger_response_compatibility(self):
        tomorrow = date.today() + timedelta(days=1)

        passenger = PassengerResponse(
            id=1,
            full_name="Nguyen Van Test",
            date_of_birth=tomorrow,
        )

        self.assertEqual(
            passenger.date_of_birth,
            tomorrow
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
