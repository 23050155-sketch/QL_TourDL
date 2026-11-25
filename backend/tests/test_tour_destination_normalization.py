
import unittest

from pydantic import ValidationError

from app.core.normalization import (
    validate_image_url,
)

from app.schemas.tour import (
    TourCreate,
    TourUpdate,
    TourResponse,
)

from app.schemas.destination import (
    DestinationCreate,
    DestinationUpdate,
    DestinationResponse,
    TourDestinationCreate,
)


class TestImageUrlValidation(unittest.TestCase):

    # 1. HTTPS hợp lệ
    def test_https_url(self):
        url = "https://example.com/Tour.JPG"
        self.assertEqual(validate_image_url(url), url)

    # 2. HTTP hợp lệ
    def test_http_url(self):
        url = "http://example.com/image.png"
        self.assertEqual(validate_image_url(url), url)

    # 3. URL có query string
    def test_query_string(self):
        url = "https://example.com/image.jpg?v=2&size=large"
        self.assertEqual(validate_image_url(url), url)

    # 4. URL null
    def test_null_url(self):
        self.assertIsNone(validate_image_url(None))

    # 5. Giao thức không được phép
    def test_invalid_schemes(self):
        values = [
            "javascript:void(0)",
            "file:///image.jpg",
            "ftp://example.com/image.jpg",
            "data:image/png;base64,AAAA",
        ]

        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_image_url(value)

    # 6. URL tương đối
    def test_relative_urls(self):
        values = [
            "/images/tour.jpg",
            "images/tour.jpg",
            "//example.com/image.jpg",
        ]

        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_image_url(value)

    # 7. URL không có hostname
    def test_missing_host(self):
        with self.assertRaises(ValueError):
            validate_image_url("https://")

    # 8. URL chứa khoảng trắng
    def test_internal_whitespace(self):
        with self.assertRaises(ValueError):
            validate_image_url(
                "https://example.com/my image.jpg"
            )

    # 9. URL chứa ký tự điều khiển
    def test_control_character(self):
        with self.assertRaises(ValueError):
            validate_image_url(
                "https://example.com/\nimage.jpg"
            )

    # 10. URL chứa dấu gạch chéo ngược
    def test_backslash(self):
        with self.assertRaises(ValueError):
            validate_image_url(
                "https://example.com\\image.jpg"
            )

    # 11. URL chứa thông tin đăng nhập
    def test_url_credentials(self):
        with self.assertRaises(ValueError):
            validate_image_url(
                "https://user:pass@example.com/image.jpg"
            )

    # 12. URL sai kiểu dữ liệu
    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            validate_image_url(123)


class TestTourNormalization(unittest.TestCase):

    def create_tour(self, **changes):
        data = {
            "title": "Tour Da Lat",
            "description": "Tour description",
            "duration_days": 3,
            "duration_nights": 2,
            "base_price": "2500000.00",
            "image_url": "https://example.com/tour.jpg",
        }

        data.update(changes)
        return TourCreate(**data)

    # 13. Chuẩn hóa tiêu đề
    def test_title_normalization(self):
        tour = self.create_tour(
            title="  Tour   Da Lat   3 Ngay  "
        )

        self.assertEqual(
            tour.title,
            "Tour Da Lat 3 Ngay"
        )

    # 14. Chuẩn hóa Unicode
    def test_title_unicode(self):
        tour = self.create_tour(
            title="Tour Cafe\u0301"
        )

        self.assertEqual(
            tour.title,
            "Tour Caf\u00e9"
        )

    # 15. Từ chối tiêu đề rỗng
    def test_blank_title(self):
        with self.assertRaises(ValidationError):
            self.create_tour(title="   ")

    # 16. Kiểm tra độ dài sau chuẩn hóa
    def test_title_too_short(self):
        with self.assertRaises(ValidationError):
            self.create_tour(title="  A  ")

    # 17. Chuẩn hóa mô tả nhiều dòng
    def test_multiline_description(self):
        tour = self.create_tour(
            description=" Day 1  \r\nDay 2  \r\nDay 3 "
        )

        self.assertEqual(
            tour.description,
            "Day 1\nDay 2\nDay 3"
        )

    # 18. Mô tả rỗng
    def test_blank_description(self):
        tour = self.create_tour(description=" \r\n ")
        self.assertIsNone(tour.description)

    # 19. Giữ nguyên khoảng trắng bên trong mô tả
    def test_description_internal_spaces(self):
        tour = self.create_tour(
            description="Day 1:   Visit museum"
        )

        self.assertEqual(
            tour.description,
            "Day 1:   Visit museum"
        )

    # 20. Chuẩn hóa URL
    def test_image_url_normalization(self):
        tour = self.create_tour(
            image_url="  https://example.com/Tour.JPG  "
        )

        self.assertEqual(
            tour.image_url,
            "https://example.com/Tour.JPG"
        )

    # 21. URL rỗng
    def test_blank_image_url(self):
        tour = self.create_tour(image_url="   ")
        self.assertIsNone(tour.image_url)

    # 22. URL null
    def test_null_image_url(self):
        tour = self.create_tour(image_url=None)
        self.assertIsNone(tour.image_url)

    # 23. URL không hợp lệ
    def test_invalid_image_url(self):
        with self.assertRaises(ValidationError):
            self.create_tour(
                image_url="ftp://example.com/image.jpg"
            )

    # 24. URL vượt giới hạn 500 ký tự
    def test_long_image_url(self):
        with self.assertRaises(ValidationError):
            self.create_tour(
                image_url="https://example.com/" + "a" * 500
            )

    # 25. TourUpdate kế thừa Normalization
    def test_tour_update_normalization(self):
        tour = TourUpdate(
            title="  Tour   Da Lat  ",
            description="   ",
            duration_days=3,
            duration_nights=2,
            base_price="2500000.00",
            image_url="  https://example.com/Tour.JPG  ",
            status="active"
        )

        self.assertEqual(tour.title, "Tour Da Lat")
        self.assertIsNone(tour.description)

        self.assertEqual(
            tour.image_url,
            "https://example.com/Tour.JPG"
        )

    # 26. Giữ nguyên kiểm tra ngày và đêm
    def test_duration_validation(self):
        with self.assertRaises(ValidationError):
            self.create_tour(
                duration_days=2,
                duration_nights=2
            )

    # 27. Giữ nguyên kiểm tra giá Tour
    def test_price_validation(self):
        with self.assertRaises(ValidationError):
            self.create_tour(base_price="-1000")

    # 28. Response tương thích dữ liệu cũ
    def test_legacy_tour_response(self):
        tour = TourResponse(
            id=1,
            title="Tour Da Lat",
            duration_days=3,
            duration_nights=2,
            base_price="2500000.00",
            image_url="/images/tour.jpg",
            status="active"
        )

        self.assertEqual(
            tour.image_url,
            "/images/tour.jpg"
        )


class TestDestinationNormalization(unittest.TestCase):

    def create_destination(self, **changes):
        data = {
            "name": "Thung Lung Tinh Yeu",
            "province": "Lam Dong",
            "description": "Destination description",
            "image_url": "https://example.com/place.jpg",
        }

        data.update(changes)
        return DestinationCreate(**data)

    # 29. Chuẩn hóa tên địa điểm
    def test_destination_name(self):
        destination = self.create_destination(
            name="  Thung   Lung   Tinh Yeu  "
        )

        self.assertEqual(
            destination.name,
            "Thung Lung Tinh Yeu"
        )

    # 30. Chuẩn hóa tỉnh thành
    def test_province(self):
        destination = self.create_destination(
            province="  Lam   Dong  "
        )

        self.assertEqual(
            destination.province,
            "Lam Dong"
        )

    # 31. Chuẩn hóa Unicode
    def test_destination_unicode(self):
        destination = self.create_destination(
            name="Cafe\u0301"
        )

        self.assertEqual(
            destination.name,
            "Caf\u00e9"
        )

    # 32. Tên địa điểm rỗng
    def test_blank_name(self):
        with self.assertRaises(ValidationError):
            self.create_destination(name="   ")

    # 33. Tỉnh thành rỗng
    def test_blank_province(self):
        with self.assertRaises(ValidationError):
            self.create_destination(province="   ")

    # 34. Chuẩn hóa mô tả
    def test_description(self):
        destination = self.create_destination(
            description=" Line 1  \r\nLine 2 "
        )

        self.assertEqual(
            destination.description,
            "Line 1\nLine 2"
        )

    # 35. Mô tả rỗng
    def test_blank_description(self):
        destination = self.create_destination(
            description="   "
        )

        self.assertIsNone(destination.description)

    # 36. Chuẩn hóa URL
    def test_image_url(self):
        destination = self.create_destination(
            image_url="  https://example.com/Place.JPG  "
        )

        self.assertEqual(
            destination.image_url,
            "https://example.com/Place.JPG"
        )

    # 37. URL rỗng
    def test_blank_url(self):
        destination = self.create_destination(
            image_url="   "
        )

        self.assertIsNone(destination.image_url)

    # 38. URL không hợp lệ
    def test_invalid_url(self):
        with self.assertRaises(ValidationError):
            self.create_destination(
                image_url="file:///image.jpg"
            )

    # 39. Chuẩn hóa dữ liệu cập nhật
    def test_destination_update(self):
        destination = DestinationUpdate(
            name="  Ho   Xuan Huong  ",
            province="  Lam   Dong  "
        )

        self.assertEqual(
            destination.name,
            "Ho Xuan Huong"
        )

        self.assertEqual(
            destination.province,
            "Lam Dong"
        )

    # 40. Không ghi đè trường không được gửi
    def test_partial_update(self):
        destination = DestinationUpdate(
            name="  Da   Lat  "
        )

        self.assertEqual(
            destination.model_dump(exclude_unset=True),
            {"name": "Da Lat"}
        )

    # 41. Xóa mô tả và hình ảnh
    def test_clear_optional_fields(self):
        destination = DestinationUpdate(
            description="   ",
            image_url="   "
        )

        self.assertEqual(
            destination.model_dump(exclude_unset=True),
            {
                "description": None,
                "image_url": None,
            }
        )

    # 42. Không cho phép tên null
    def test_null_name(self):
        with self.assertRaises(ValidationError):
            DestinationUpdate(name=None)

    # 43. Không cho phép tỉnh thành null
    def test_null_province(self):
        with self.assertRaises(ValidationError):
            DestinationUpdate(province=None)

    # 44. URL cập nhật không hợp lệ
    def test_update_invalid_url(self):
        with self.assertRaises(ValidationError):
            DestinationUpdate(
                image_url="/images/place.jpg"
            )

    # 45. Response tương thích dữ liệu cũ
    def test_legacy_destination_response(self):
        destination = DestinationResponse(
            id=1,
            name="Da Lat",
            province="Lam Dong",
            image_url="/images/place.jpg"
        )

        self.assertEqual(
            destination.image_url,
            "/images/place.jpg"
        )

    # 46. Giữ nguyên liên kết Tour - Destination
    def test_tour_destination_create(self):
        data = TourDestinationCreate(
            destination_id=1,
            visit_order=2
        )

        self.assertEqual(data.destination_id, 1)
        self.assertEqual(data.visit_order, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
