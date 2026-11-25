
import unittest

from datetime import date, timedelta

from pydantic import ValidationError

from app.schemas.booking import (
    PassengerCreate,
    PassengerResponse,
    BookingCreate,
)

from app.schemas.guide import (
    GuideCreate,
    GuideUpdate,
    GuidePublicResponse,
    GuideContactResponse,
)


class TestBookingNormalization(unittest.TestCase):

    # 1. Chuẩn hóa họ tên
    def test_passenger_name(self):
        passenger = PassengerCreate(
            full_name="  Nguyen   Van   An  "
        )

        self.assertEqual(
            passenger.full_name,
            "Nguyen Van An"
        )

    # 2. Chuẩn hóa Unicode
    def test_passenger_unicode(self):
        passenger = PassengerCreate(
            full_name="Cafe\u0301"
        )

        self.assertEqual(
            passenger.full_name,
            "Caf\u00e9"
        )

    # 3. Từ chối họ tên rỗng
    def test_blank_passenger_name(self):
        with self.assertRaises(ValidationError):
            PassengerCreate(full_name="   ")

    # 4. Chuẩn hóa số điện thoại
    def test_passenger_phone(self):
        passenger = PassengerCreate(
            full_name="Nguyen Van An",
            phone="090-123-4567"
        )

        self.assertEqual(
            passenger.phone,
            "0901234567"
        )

    # 5. Số điện thoại quốc tế
    def test_international_phone(self):
        passenger = PassengerCreate(
            full_name="Nguyen Van An",
            phone="+84 901 234 567"
        )

        self.assertEqual(
            passenger.phone,
            "+84901234567"
        )

    # 6. Số điện thoại rỗng
    def test_blank_phone(self):
        passenger = PassengerCreate(
            full_name="Nguyen Van An",
            phone="   "
        )

        self.assertIsNone(passenger.phone)

    # 7. Số điện thoại null
    def test_null_phone(self):
        passenger = PassengerCreate(
            full_name="Nguyen Van An",
            phone=None
        )

        self.assertIsNone(passenger.phone)

    # 8. Số điện thoại không hợp lệ
    def test_invalid_phone(self):
        values = [
            "abc123",
            "123",
            "---",
            "1" * 16,
            901234567,
        ]

        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    PassengerCreate(
                        full_name="Nguyen Van An",
                        phone=value
                    )

    # 9. Giữ nguyên kiểm tra ngày sinh
    def test_future_birth_date(self):
        with self.assertRaises(ValidationError):
            PassengerCreate(
                full_name="Nguyen Van An",
                date_of_birth=(
                    date.today() + timedelta(days=1)
                )
            )

    # 10. Chuẩn hóa nhiều hành khách
    def test_booking_nested_normalization(self):
        booking = BookingCreate(
            schedule_id=1,
            number_of_people=2,
            passengers=[
                {
                    "full_name": "  Nguyen   Van An  ",
                    "phone": "090-123-4567",
                },
                {
                    "full_name": "  Tran   Thi Binh  ",
                    "phone": "091 234 5678",
                },
            ]
        )

        self.assertEqual(
            booking.passengers[0].full_name,
            "Nguyen Van An"
        )

        self.assertEqual(
            booking.passengers[0].phone,
            "0901234567"
        )

        self.assertEqual(
            booking.passengers[1].full_name,
            "Tran Thi Binh"
        )

        self.assertEqual(
            booking.passengers[1].phone,
            "0912345678"
        )

    # 11. Từ chối Booking có hành khách không hợp lệ
    def test_invalid_nested_passenger(self):
        with self.assertRaises(ValidationError):
            BookingCreate(
                schedule_id=1,
                number_of_people=2,
                passengers=[
                    {
                        "full_name": "Nguyen Van An",
                        "phone": "0901234567",
                    },
                    {
                        "full_name": "Tran Thi Binh",
                        "phone": "abc123",
                    },
                ]
            )

    # 12. Giữ nguyên kiểm tra số lượng hành khách
    def test_passenger_count_mismatch(self):
        with self.assertRaises(ValidationError):
            BookingCreate(
                schedule_id=1,
                number_of_people=2,
                passengers=[
                    {
                        "full_name": "Nguyen Van An"
                    }
                ]
            )

    # 13. Response không làm thay đổi dữ liệu cũ
    def test_passenger_response_compatibility(self):
        passenger = PassengerResponse(
            id=1,
            full_name="Nguyen Van An",
            phone="090-123-4567"
        )

        self.assertEqual(
            passenger.phone,
            "090-123-4567"
        )


class TestGuideNormalization(unittest.TestCase):

    # 14. Chuẩn hóa họ tên hướng dẫn viên
    def test_guide_name(self):
        guide = GuideCreate(
            full_name="  Nguyen   Van Minh  "
        )

        self.assertEqual(
            guide.full_name,
            "Nguyen Van Minh"
        )

    # 15. Chuẩn hóa Unicode
    def test_guide_unicode(self):
        guide = GuideCreate(
            full_name="Cafe\u0301"
        )

        self.assertEqual(
            guide.full_name,
            "Caf\u00e9"
        )

    # 16. Chuẩn hóa số điện thoại
    def test_guide_phone(self):
        guide = GuideCreate(
            full_name="Nguyen Van Minh",
            phone="+84 901-234-567"
        )

        self.assertEqual(
            guide.phone,
            "+84901234567"
        )

    # 17. Chuẩn hóa email
    def test_guide_email(self):
        guide = GuideCreate(
            full_name="Nguyen Van Minh",
            email="  GUIDE@EXAMPLE.COM  "
        )

        self.assertEqual(
            guide.email,
            "guide@example.com"
        )

    # 18. Email rỗng
    def test_blank_email(self):
        guide = GuideCreate(
            full_name="Nguyen Van Minh",
            email="   "
        )

        self.assertIsNone(guide.email)

    # 19. Email null
    def test_null_email(self):
        guide = GuideCreate(
            full_name="Nguyen Van Minh",
            email=None
        )

        self.assertIsNone(guide.email)

    # 20. Email không hợp lệ
    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            GuideCreate(
                full_name="Nguyen Van Minh",
                email="invalid-email"
            )

    # 21. Email vượt giới hạn Database
    def test_long_email(self):
        email = (
            "a" * 60
            + "@"
            + "b" * 60
            + "."
            + "c" * 60
            + "."
            + "d" * 20
            + ".com"
        )

        with self.assertRaises(ValidationError):
            GuideCreate(
                full_name="Nguyen Van Minh",
                email=email
            )

    # 22. Số điện thoại không hợp lệ
    def test_invalid_guide_phone(self):
        with self.assertRaises(ValidationError):
            GuideCreate(
                full_name="Nguyen Van Minh",
                phone="abc123"
            )

    # 23. Chuẩn hóa dữ liệu cập nhật
    def test_guide_update(self):
        guide = GuideUpdate(
            full_name="  Nguyen   Van Minh  ",
            phone="090-123-4567",
            email="  GUIDE@EXAMPLE.COM  "
        )

        self.assertEqual(
            guide.full_name,
            "Nguyen Van Minh"
        )

        self.assertEqual(
            guide.phone,
            "0901234567"
        )

        self.assertEqual(
            guide.email,
            "guide@example.com"
        )

    # 24. Xóa thông tin liên hệ
    def test_clear_contact(self):
        guide = GuideUpdate(
            phone="   ",
            email="   "
        )

        self.assertEqual(
            guide.model_dump(exclude_unset=True),
            {
                "phone": None,
                "email": None,
            }
        )

    # 25. Không ghi đè trường không được gửi
    def test_partial_update(self):
        guide = GuideUpdate(
            experience_years=5
        )

        self.assertEqual(
            guide.model_dump(exclude_unset=True),
            {"experience_years": 5}
        )

    # 26. Không cho phép họ tên null
    def test_null_name(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(full_name=None)

    # 27. Không cho phép họ tên rỗng
    def test_blank_name(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(full_name="   ")

    # 28. Không cho phép trạng thái null
    def test_null_status(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(status=None)

    # 29. Giữ nguyên giới hạn kinh nghiệm
    def test_invalid_experience(self):
        with self.assertRaises(ValidationError):
            GuideCreate(
                full_name="Nguyen Van Minh",
                experience_years=81
            )

    # 30. Email cập nhật không hợp lệ
    def test_update_invalid_email(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(email="invalid-email")

    # 31. Bảo mật Response công khai
    def test_public_response_privacy(self):
        guide = GuidePublicResponse(
            id=1,
            full_name="Nguyen Van Minh",
            experience_years=5,
            phone="0901234567",
            email="guide@example.com"
        )

        data = guide.model_dump()

        self.assertNotIn("phone", data)
        self.assertNotIn("email", data)

    # 32. Response liên hệ giữ nguyên dữ liệu cũ
    def test_contact_response_compatibility(self):
        guide = GuideContactResponse(
            id=1,
            full_name="Nguyen Van Minh",
            experience_years=5,
            phone="090-123-4567",
            email="GUIDE@EXAMPLE.COM"
        )

        self.assertEqual(
            guide.phone,
            "090-123-4567"
        )

        self.assertEqual(
            guide.email,
            "GUIDE@EXAMPLE.COM"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
