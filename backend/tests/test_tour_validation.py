
import unittest

from decimal import Decimal

from pydantic import ValidationError

from app.schemas.tour import (
    TourCreate,
    TourUpdate,
    TourResponse,
)

from app.core.validation import (
    MAX_TOUR_DURATION_DAYS,
    MAX_TOUR_DURATION_NIGHTS,
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGE_URL_LENGTH,
)


class TestTourValidation(unittest.TestCase):

    def valid_tour(self):
        return {
            "title": "Tour Da Lat Test",
            "description": "Tour kiem thu",
            "duration_days": 3,
            "duration_nights": 2,
            "base_price": "1500000.00",
            "image_url": None,
        }

    # Hàm hỗ trợ kiểm tra dữ liệu không hợp lệ
    def assert_invalid(self, **changes):
        data = self.valid_tour()
        data.update(changes)

        with self.assertRaises(ValidationError):
            TourCreate(**data)

    # 1. Tour hợp lệ
    def test_valid_tour(self):
        tour = TourCreate(**self.valid_tour())

        self.assertEqual(tour.duration_days, 3)
        self.assertEqual(tour.duration_nights, 2)
        self.assertEqual(
            tour.base_price,
            Decimal("1500000.00")
        )

    # 2. Tour trong ngày
    def test_one_day_tour(self):
        data = self.valid_tour()
        data["duration_days"] = 1
        data["duration_nights"] = 0

        tour = TourCreate(**data)

        self.assertEqual(tour.duration_nights, 0)

    # 3. Số ngày bằng 0
    def test_zero_days(self):
        self.assert_invalid(duration_days=0)

    # 4. Số ngày vượt giới hạn
    def test_too_many_days(self):
        self.assert_invalid(
            duration_days=MAX_TOUR_DURATION_DAYS + 1
        )

    # 5. Số đêm âm
    def test_negative_nights(self):
        self.assert_invalid(duration_nights=-1)

    # 6. Số đêm vượt giới hạn
    def test_too_many_nights(self):
        self.assert_invalid(
            duration_days=MAX_TOUR_DURATION_DAYS,
            duration_nights=MAX_TOUR_DURATION_NIGHTS + 1
        )

    # 7. Số đêm bằng số ngày
    def test_equal_days_and_nights(self):
        self.assert_invalid(duration_nights=3)

    # 8. Số đêm lớn hơn số ngày
    def test_nights_greater_than_days(self):
        self.assert_invalid(duration_nights=4)

    # 9. Số ngày dạng chuỗi
    def test_string_days(self):
        self.assert_invalid(duration_days="3")

    # 10. Số ngày dạng boolean
    def test_boolean_days(self):
        self.assert_invalid(duration_days=True)

    # 11. Số đêm dạng số thực
    def test_float_nights(self):
        self.assert_invalid(duration_nights=1.5)

    # 12. Giá Tour bằng 0
    def test_zero_price(self):
        self.assert_invalid(base_price="0")

    # 13. Giá Tour âm
    def test_negative_price(self):
        self.assert_invalid(base_price="-1000")

    # 14. Giá Tour vượt giới hạn MySQL
    def test_price_overflow(self):
        self.assert_invalid(
            base_price="10000000000.00"
        )

    # 15. Giá có quá 2 chữ số thập phân
    def test_invalid_decimal_places(self):
        self.assert_invalid(base_price="1000.123")

    # 16. Mô tả vượt giới hạn
    def test_description_too_long(self):
        self.assert_invalid(
            description="A" * (MAX_DESCRIPTION_LENGTH + 1)
        )

    # 17. URL ảnh vượt giới hạn
    def test_image_url_too_long(self):
        self.assert_invalid(
            image_url="A" * (MAX_IMAGE_URL_LENGTH + 1)
        )

    # 18. Trường dư thừa
    def test_extra_field(self):
        self.assert_invalid(id=1)

    # 19. Cập nhật Tour hợp lệ
    def test_valid_tour_update(self):
        data = self.valid_tour()
        data["status"] = "active"

        tour = TourUpdate(**data)

        self.assertEqual(tour.status, "active")

    # 20. Trạng thái không hợp lệ
    def test_invalid_status(self):
        data = self.valid_tour()
        data["status"] = "unknown"

        with self.assertRaises(ValidationError):
            TourUpdate(**data)

    # 21. TourUpdate kế thừa Validator
    def test_update_invalid_duration(self):
        data = self.valid_tour()
        data["status"] = "active"
        data["duration_nights"] = 3

        with self.assertRaises(ValidationError):
            TourUpdate(**data)

    # 22. TourUpdate kế thừa extra="forbid"
    def test_update_extra_field(self):
        data = self.valid_tour()
        data["status"] = "active"
        data["id"] = 1

        with self.assertRaises(ValidationError):
            TourUpdate(**data)

    # 23. Giới hạn thời lượng hợp lệ
    def test_valid_max_duration(self):
        data = self.valid_tour()

        data["duration_days"] = MAX_TOUR_DURATION_DAYS
        data["duration_nights"] = MAX_TOUR_DURATION_NIGHTS

        tour = TourCreate(**data)

        self.assertEqual(
            tour.duration_days,
            MAX_TOUR_DURATION_DAYS
        )

    # 24. Response tương thích dữ liệu cũ
    def test_response_compatibility(self):
        data = self.valid_tour()
        data["id"] = 1
        data["status"] = "active"
        data["duration_nights"] = 3

        tour = TourResponse(**data)

        self.assertEqual(tour.duration_nights, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
