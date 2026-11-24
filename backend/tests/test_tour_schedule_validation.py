
import unittest

from datetime import date, timedelta

from pydantic import ValidationError

from app.schemas.tour_schedule import (
    TourScheduleCreate,
    TourScheduleUpdate,
    TourScheduleResponse,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_SCHEDULE_CAPACITY,
    MAX_TOUR_DURATION_DAYS,
)


class TestTourScheduleValidation(unittest.TestCase):

    def valid_schedule(self):
        departure = date.today() + timedelta(days=10)

        return {
            "tour_id": 1,
            "departure_date": departure,
            "return_date": departure + timedelta(days=2),
            "capacity": 35,
        }

    # Hàm hỗ trợ kiểm tra dữ liệu không hợp lệ
    def assert_invalid(self, **changes):
        data = self.valid_schedule()
        data.update(changes)

        with self.assertRaises(ValidationError):
            TourScheduleCreate(**data)

    # 1. Lịch khởi hành hợp lệ
    def test_valid_schedule(self):
        schedule = TourScheduleCreate(
            **self.valid_schedule()
        )

        self.assertEqual(schedule.capacity, 35)

    # 2. ID bằng 0
    def test_zero_tour_id(self):
        self.assert_invalid(tour_id=0)

    # 3. ID âm
    def test_negative_tour_id(self):
        self.assert_invalid(tour_id=-1)

    # 4. ID vượt giới hạn MySQL
    def test_tour_id_overflow(self):
        self.assert_invalid(
            tour_id=MAX_UNSIGNED_BIGINT + 1
        )

    # 5. ID dạng chuỗi
    def test_string_tour_id(self):
        self.assert_invalid(tour_id="1")

    # 6. ID dạng boolean
    def test_boolean_tour_id(self):
        self.assert_invalid(tour_id=True)

    # 7. Sức chứa bằng 0
    def test_zero_capacity(self):
        self.assert_invalid(capacity=0)

    # 8. Sức chứa âm
    def test_negative_capacity(self):
        self.assert_invalid(capacity=-10)

    # 9. Sức chứa vượt giới hạn
    def test_capacity_overflow(self):
        self.assert_invalid(
            capacity=MAX_SCHEDULE_CAPACITY + 1
        )

    # 10. Sức chứa dạng chuỗi
    def test_string_capacity(self):
        self.assert_invalid(capacity="35")

    # 11. Sức chứa dạng boolean
    def test_boolean_capacity(self):
        self.assert_invalid(capacity=True)

    # 12. Sức chứa dạng số thực
    def test_float_capacity(self):
        self.assert_invalid(capacity=35.5)

    # 13. Sức chứa tối đa hợp lệ
    def test_valid_max_capacity(self):
        data = self.valid_schedule()
        data["capacity"] = MAX_SCHEDULE_CAPACITY

        schedule = TourScheduleCreate(**data)

        self.assertEqual(
            schedule.capacity,
            MAX_SCHEDULE_CAPACITY
        )

    # 14. Ngày kết thúc trước ngày khởi hành
    def test_invalid_date_order(self):
        data = self.valid_schedule()

        data["return_date"] = (
            data["departure_date"] - timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            TourScheduleCreate(**data)

    # 15. Tour đi và về trong cùng ngày
    def test_same_day_schedule(self):
        data = self.valid_schedule()

        data["return_date"] = data["departure_date"]

        schedule = TourScheduleCreate(**data)

        self.assertEqual(
            schedule.departure_date,
            schedule.return_date
        )

    # 16. Ngày không tồn tại
    def test_invalid_date(self):
        self.assert_invalid(
            departure_date="2026-02-30"
        )

    # 17. Thời lượng vượt giới hạn
    def test_duration_overflow(self):
        data = self.valid_schedule()

        data["return_date"] = (
            data["departure_date"]
            + timedelta(days=MAX_TOUR_DURATION_DAYS)
        )

        with self.assertRaises(ValidationError):
            TourScheduleCreate(**data)

    # 18. Thời lượng tối đa hợp lệ
    def test_valid_max_duration(self):
        data = self.valid_schedule()

        data["return_date"] = (
            data["departure_date"]
            + timedelta(
                days=MAX_TOUR_DURATION_DAYS - 1
            )
        )

        schedule = TourScheduleCreate(**data)

        duration = (
            schedule.return_date
            - schedule.departure_date
        ).days + 1

        self.assertEqual(
            duration,
            MAX_TOUR_DURATION_DAYS
        )

    # 19. Trường dư thừa
    def test_extra_field(self):
        self.assert_invalid(booked_slots=10)

    # 20. Cập nhật lịch hợp lệ
    def test_valid_update(self):
        data = self.valid_schedule()
        data["status"] = "closed"

        schedule = TourScheduleUpdate(**data)

        self.assertEqual(schedule.status, "closed")

    # 21. Trạng thái không hợp lệ
    def test_invalid_status(self):
        data = self.valid_schedule()
        data["status"] = "unknown"

        with self.assertRaises(ValidationError):
            TourScheduleUpdate(**data)

    # 22. Update kế thừa giới hạn sức chứa
    def test_update_invalid_capacity(self):
        data = self.valid_schedule()
        data["status"] = "open"
        data["capacity"] = MAX_SCHEDULE_CAPACITY + 1

        with self.assertRaises(ValidationError):
            TourScheduleUpdate(**data)

    # 23. Update kế thừa extra="forbid"
    def test_update_extra_field(self):
        data = self.valid_schedule()
        data["status"] = "open"
        data["remaining_slots"] = 100

        with self.assertRaises(ValidationError):
            TourScheduleUpdate(**data)

    # 24. Response tương thích dữ liệu lịch sử
    def test_response_compatibility(self):
        data = self.valid_schedule()

        data.update({
            "id": 1,
            "capacity": MAX_SCHEDULE_CAPACITY + 1,
            "status": "open",
            "booked_slots": 0,
            "remaining_slots": MAX_SCHEDULE_CAPACITY + 1,
            "is_full": False,
            "is_bookable": True,
        })

        schedule = TourScheduleResponse(**data)

        self.assertEqual(
            schedule.capacity,
            MAX_SCHEDULE_CAPACITY + 1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
