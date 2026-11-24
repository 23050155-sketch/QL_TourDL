
import unittest

from pydantic import ValidationError

from app.schemas.destination import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    TourDestinationCreate,
)

from app.schemas.guide import (
    GuideCreate,
    GuideUpdate,
    GuidePublicResponse,
    GuideContactResponse,
    GuideResponse,
    GuideAssignmentCreate,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_SIGNED_INT,
    MAX_DESCRIPTION_LENGTH,
    MAX_IMAGE_URL_LENGTH,
    MAX_GUIDE_EXPERIENCE_YEARS,
)


class TestDestinationValidation(unittest.TestCase):

    def valid_destination(self):
        return {
            "name": "Da Lat",
            "province": "Lam Dong",
            "description": "Dia diem kiem thu",
            "image_url": None,
        }

    def assert_invalid(self, **changes):
        data = self.valid_destination()
        data.update(changes)

        with self.assertRaises(ValidationError):
            DestinationCreate(**data)

    # 1. Địa điểm hợp lệ
    def test_valid_destination(self):
        destination = DestinationCreate(
            **self.valid_destination()
        )

        self.assertEqual(destination.name, "Da Lat")

    # 2. Tên quá ngắn
    def test_short_name(self):
        self.assert_invalid(name="A")

    # 3. Tỉnh thành quá dài
    def test_long_province(self):
        self.assert_invalid(province="A" * 151)

    # 4. Mô tả vượt giới hạn
    def test_long_description(self):
        self.assert_invalid(
            description="A" * (MAX_DESCRIPTION_LENGTH + 1)
        )

    # 5. URL vượt giới hạn
    def test_long_image_url(self):
        self.assert_invalid(
            image_url="A" * (MAX_IMAGE_URL_LENGTH + 1)
        )

    # 6. Trường dư thừa
    def test_extra_field(self):
        self.assert_invalid(id=1)

    # 7. Cập nhật một thuộc tính
    def test_partial_update(self):
        destination = DestinationUpdate(
            name="Nha Trang"
        )

        self.assertEqual(
            destination.model_dump(exclude_unset=True),
            {"name": "Nha Trang"}
        )

    # 8. Tên không được là null
    def test_null_name(self):
        with self.assertRaises(ValidationError):
            DestinationUpdate(name=None)

    # 9. Tỉnh thành không được là null
    def test_null_province(self):
        with self.assertRaises(ValidationError):
            DestinationUpdate(province=None)

    # 10. Cho phép xóa mô tả
    def test_null_description(self):
        destination = DestinationUpdate(
            description=None
        )

        self.assertEqual(
            destination.model_dump(exclude_unset=True),
            {"description": None}
        )

    # 11. Cho phép xóa URL ảnh
    def test_null_image_url(self):
        destination = DestinationUpdate(
            image_url=None
        )

        self.assertIsNone(destination.image_url)

    # 12. Response tương thích dữ liệu lịch sử
    def test_response_compatibility(self):
        data = self.valid_destination()

        data["id"] = 1
        data["description"] = (
            "A" * (MAX_DESCRIPTION_LENGTH + 1)
        )

        destination = DestinationResponse(**data)

        self.assertEqual(
            len(destination.description),
            MAX_DESCRIPTION_LENGTH + 1
        )


class TestTourDestinationValidation(unittest.TestCase):

    # 13. Liên kết địa điểm hợp lệ
    def test_valid_tour_destination(self):
        destination = TourDestinationCreate(
            destination_id=1
        )

        self.assertEqual(destination.visit_order, 1)

    # 14. ID bằng 0
    def test_zero_destination_id(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(destination_id=0)

    # 15. ID vượt giới hạn MySQL
    def test_destination_id_overflow(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(
                destination_id=MAX_UNSIGNED_BIGINT + 1
            )

    # 16. ID dạng chuỗi
    def test_string_destination_id(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(destination_id="1")

    # 17. Thứ tự tham quan bằng 0
    def test_zero_visit_order(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(
                destination_id=1,
                visit_order=0
            )

    # 18. Thứ tự tham quan vượt giới hạn
    def test_visit_order_overflow(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(
                destination_id=1,
                visit_order=MAX_SIGNED_INT + 1
            )

    # 19. Thứ tự tham quan dạng boolean
    def test_boolean_visit_order(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(
                destination_id=1,
                visit_order=True
            )

    # 20. Trường dư thừa
    def test_extra_field(self):
        with self.assertRaises(ValidationError):
            TourDestinationCreate(
                destination_id=1,
                tour_id=2
            )


class TestGuideValidation(unittest.TestCase):

    def valid_guide(self):
        return {
            "full_name": "Nguyen Van Test",
            "phone": "0900000000",
            "email": "guide@example.com",
            "experience_years": 5,
        }

    def assert_invalid(self, **changes):
        data = self.valid_guide()
        data.update(changes)

        with self.assertRaises(ValidationError):
            GuideCreate(**data)

    # 21. Hướng dẫn viên hợp lệ
    def test_valid_guide(self):
        guide = GuideCreate(**self.valid_guide())

        self.assertEqual(guide.experience_years, 5)

    # 22. Kinh nghiệm âm
    def test_negative_experience(self):
        self.assert_invalid(experience_years=-1)

    # 23. Kinh nghiệm vượt giới hạn
    def test_experience_overflow(self):
        self.assert_invalid(
            experience_years=MAX_GUIDE_EXPERIENCE_YEARS + 1
        )

    # 24. Kinh nghiệm dạng chuỗi
    def test_string_experience(self):
        self.assert_invalid(experience_years="5")

    # 25. Kinh nghiệm dạng boolean
    def test_boolean_experience(self):
        self.assert_invalid(experience_years=True)

    # 26. Kinh nghiệm tối đa hợp lệ
    def test_max_experience(self):
        data = self.valid_guide()

        data["experience_years"] = (
            MAX_GUIDE_EXPERIENCE_YEARS
        )

        guide = GuideCreate(**data)

        self.assertEqual(
            guide.experience_years,
            MAX_GUIDE_EXPERIENCE_YEARS
        )

    # 27. Email quá dài
    def test_long_email(self):
        self.assert_invalid(email="A" * 191)

    # 28. Số điện thoại quá dài
    def test_long_phone(self):
        self.assert_invalid(phone="0" * 21)

    # 29. Trường dư thừa
    def test_extra_field(self):
        self.assert_invalid(status="active")

    # 30. Cập nhật trạng thái hợp lệ
    def test_valid_status_update(self):
        guide = GuideUpdate(status="inactive")

        self.assertEqual(guide.status, "inactive")

    # 31. Trạng thái không hợp lệ
    def test_invalid_status(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(status="unknown")

    # 32. Không cho phép status null
    def test_null_status(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(status=None)

    # 33. Không cho phép full_name null
    def test_null_full_name(self):
        with self.assertRaises(ValidationError):
            GuideUpdate(full_name=None)

    # 34. Cho phép email null
    def test_null_email(self):
        guide = GuideUpdate(email=None)

        self.assertEqual(
            guide.model_dump(exclude_unset=True),
            {"email": None}
        )

    # 35. Cho phép kinh nghiệm null
    def test_null_experience(self):
        guide = GuideUpdate(experience_years=None)

        self.assertIsNone(guide.experience_years)

    # 36. Response công khai không chứa liên hệ
    def test_public_response_privacy(self):
        guide = GuidePublicResponse(
            id=1,
            **self.valid_guide()
        )

        data = guide.model_dump()

        self.assertNotIn("phone", data)
        self.assertNotIn("email", data)

    # 37. Response liên hệ có phone và email
    def test_contact_response(self):
        guide = GuideContactResponse(
            id=1,
            **self.valid_guide()
        )

        data = guide.model_dump()

        self.assertIn("phone", data)
        self.assertIn("email", data)
        self.assertNotIn("status", data)

    # 38. Response Admin đầy đủ
    def test_admin_response(self):
        guide = GuideResponse(
            id=1,
            status="active",
            **self.valid_guide()
        )

        self.assertEqual(guide.status, "active")
        self.assertIsNotNone(guide.email)


class TestGuideAssignmentValidation(unittest.TestCase):

    # 39. Phân công hợp lệ
    def test_valid_assignment(self):
        assignment = GuideAssignmentCreate(
            schedule_id=1,
            guide_id=1
        )

        self.assertEqual(assignment.guide_id, 1)

    # 40. ID lịch bằng 0
    def test_zero_schedule_id(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id=0,
                guide_id=1
            )

    # 41. ID HDV bằng 0
    def test_zero_guide_id(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id=1,
                guide_id=0
            )

    # 42. ID vượt giới hạn
    def test_guide_id_overflow(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id=1,
                guide_id=MAX_UNSIGNED_BIGINT + 1
            )

    # 43. ID dạng chuỗi
    def test_string_schedule_id(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id="1",
                guide_id=1
            )

    # 44. ID dạng boolean
    def test_boolean_guide_id(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id=1,
                guide_id=True
            )

    # 45. Trường dư thừa
    def test_extra_field(self):
        with self.assertRaises(ValidationError):
            GuideAssignmentCreate(
                schedule_id=1,
                guide_id=1,
                id=100
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
