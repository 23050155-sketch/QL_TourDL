
import unittest

from fastapi import HTTPException
from pydantic import ValidationError

from app.core.text_validation import (
    validate_text_characters,
    validate_single_line_text,
    validate_multiline_text,
    validate_identifier_text,
)

from app.core.normalization import (
    normalize_single_line,
    normalize_optional_multiline,
    normalize_email,
    normalize_phone,
    normalize_transaction_code,
    normalize_optional_url,
    validate_image_url,
)

from app.core.search_validation import (
    normalize_search_keyword,
)

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)

from app.schemas.user import ProfileUpdate
from app.schemas.booking import PassengerCreate
from app.schemas.guide import GuideCreate
from app.schemas.tour import TourCreate
from app.schemas.destination import DestinationCreate
from app.schemas.review import ReviewCreate
from app.schemas.payment import PaymentConfirm


# ==================================================
# 1. TEXT CHARACTER VALIDATION
# ==================================================

class TestTextCharacters(unittest.TestCase):

    def test_vietnamese(self):
        value = "Nguyễn Văn An"
        self.assertEqual(
            validate_single_line_text(value),
            value,
        )

    def test_emoji(self):
        value = "Tour Đà Lạt 🌍"
        self.assertEqual(
            validate_multiline_text(value),
            value,
        )

    def test_punctuation(self):
        value = "A & B < C > D"
        self.assertEqual(
            validate_single_line_text(value),
            value,
        )

    def test_none(self):
        self.assertIsNone(
            validate_text_characters(None)
        )

    def test_non_string(self):
        self.assertEqual(
            validate_text_characters(123),
            123,
        )

    def test_empty_string(self):
        self.assertEqual(
            validate_text_characters(""),
            "",
        )

    def test_single_line_whitespace(self):
        value = "Nguyễn\tVăn\nAn"
        self.assertEqual(
            validate_single_line_text(value),
            value,
        )

    def test_multiline(self):
        value = "Dòng 1\r\nDòng 2\tNội dung"
        self.assertEqual(
            validate_multiline_text(value),
            value,
        )

    def test_null_character(self):
        with self.assertRaises(ValueError):
            validate_single_line_text("Test\x00")

    def test_escape_character(self):
        with self.assertRaises(ValueError):
            validate_multiline_text("Test\x1b")

    def test_del_character(self):
        with self.assertRaises(ValueError):
            validate_single_line_text("Test\x7f")

    def test_c1_control(self):
        with self.assertRaises(ValueError):
            validate_multiline_text("Test\x85")

    def test_vertical_tab(self):
        with self.assertRaises(ValueError):
            validate_single_line_text("Test\x0b")

    def test_surrogate(self):
        with self.assertRaises(ValueError):
            validate_multiline_text("Test\ud800")

    def test_identifier_valid(self):
        value = "TX-AbC-001"
        self.assertEqual(
            validate_identifier_text(value),
            value,
        )

    def test_identifier_newline(self):
        with self.assertRaises(ValueError):
            validate_identifier_text("TX\n001")

    def test_identifier_tab(self):
        with self.assertRaises(ValueError):
            validate_identifier_text("TX\t001")


# ==================================================
# 2. NORMALIZATION SECURITY
# ==================================================

class TestTextNormalization(unittest.TestCase):

    def test_single_line_normalization(self):
        self.assertEqual(
            normalize_single_line(
                "  Nguyễn\tVăn\nAn  "
            ),
            "Nguyễn Văn An",
        )

    def test_single_line_control(self):
        with self.assertRaises(ValueError):
            normalize_single_line("Nguyễn\x00An")

    def test_multiline_normalization(self):
        self.assertEqual(
            normalize_optional_multiline(
                "  Dòng 1\r\nDòng 2  "
            ),
            "Dòng 1\nDòng 2",
        )

    def test_multiline_control(self):
        with self.assertRaises(ValueError):
            normalize_optional_multiline(
                "Nội dung\x1b"
            )

    def test_blank_multiline(self):
        self.assertIsNone(
            normalize_optional_multiline(" \n\t ")
        )

    def test_plain_text_preserved(self):
        value = "<b>Tour Đà Lạt</b> & thiên nhiên"

        self.assertEqual(
            normalize_optional_multiline(value),
            value,
        )

    def test_email_normalization(self):
        self.assertEqual(
            normalize_email(" USER@EXAMPLE.COM "),
            "user@example.com",
        )

    def test_email_newline(self):
        with self.assertRaises(ValueError):
            normalize_email("user@example.com\n")

    def test_phone_normalization(self):
        self.assertEqual(
            normalize_phone("090-123-4567"),
            "0901234567",
        )

    def test_phone_tab(self):
        with self.assertRaises(ValueError):
            normalize_phone("090\t1234567")

    def test_transaction_normalization(self):
        self.assertEqual(
            normalize_transaction_code(
                "  TX-AbC-001  "
            ),
            "TX-AbC-001",
        )

    def test_transaction_leading_zeros(self):
        self.assertEqual(
            normalize_transaction_code("000123"),
            "000123",
        )

    def test_transaction_newline(self):
        with self.assertRaises(ValueError):
            normalize_transaction_code("TX\n001")

    def test_search_control(self):
        with self.assertRaises(HTTPException) as ctx:
            normalize_search_keyword("Tour\x00")

        self.assertEqual(
            ctx.exception.status_code,
            422,
        )

    def test_search_surrogate(self):
        with self.assertRaises(HTTPException) as ctx:
            normalize_search_keyword("Tour\ud800")

        self.assertEqual(
            ctx.exception.status_code,
            422,
        )


# ==================================================
# 3. IMAGE URL SECURITY
# ==================================================

class TestImageURLSecurity(unittest.TestCase):

    def normalize_and_validate(self, value):
        return validate_image_url(
            normalize_optional_url(value)
        )

    def test_https(self):
        value = "https://example.com/tour.jpg"

        self.assertEqual(
            self.normalize_and_validate(value),
            value,
        )

    def test_http(self):
        value = "http://example.com/tour.jpg"

        self.assertEqual(
            self.normalize_and_validate(value),
            value,
        )

    def test_trim(self):
        self.assertEqual(
            self.normalize_and_validate(
                " https://example.com/tour.jpg "
            ),
            "https://example.com/tour.jpg",
        )

    def test_query_string(self):
        value = "https://example.com/image?id=1"

        self.assertEqual(
            self.normalize_and_validate(value),
            value,
        )

    def test_encoded_space(self):
        value = "https://example.com/my%20image.jpg"

        self.assertEqual(
            self.normalize_and_validate(value),
            value,
        )

    def test_none(self):
        self.assertIsNone(
            self.normalize_and_validate(None)
        )

    def test_blank(self):
        self.assertIsNone(
            self.normalize_and_validate("   ")
        )

    def test_ftp(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "ftp://example.com/image.jpg"
            )

    def test_file_url(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "file:///image.jpg"
            )

    def test_data_url(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "data:image/png;base64,AAAA"
            )

    def test_relative_url(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "/images/tour.jpg"
            )

    def test_protocol_relative(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "//example.com/image.jpg"
            )

    def test_missing_host(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate("https://")

    def test_malformed_authority(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https:///example.com"
            )

    def test_internal_space(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com/my image.jpg"
            )

    def test_trailing_newline(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com/image.jpg\n"
            )

    def test_leading_tab(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "\thttps://example.com/image.jpg"
            )

    def test_null_character(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com/\x00image.jpg"
            )

    def test_c1_control(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com/\x85image.jpg"
            )

    def test_surrogate(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com/\ud800"
            )

    def test_backslash(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://example.com\\image.jpg"
            )

    def test_credentials(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(
                "https://user:pass@example.com/image.jpg"
            )

    def test_numeric_input(self):
        with self.assertRaises(ValueError):
            self.normalize_and_validate(123)


# ==================================================
# 4. REQUEST SCHEMA INTEGRATION
# ==================================================

class TestSchemaTextSecurity(unittest.TestCase):

    def assert_invalid_field(
        self,
        schema,
        data,
        field_name,
    ):
        with self.assertRaises(ValidationError) as ctx:
            schema.model_validate(data)

        locations = [
            error["loc"]
            for error in ctx.exception.errors()
        ]

        self.assertIn(
            (field_name,),
            locations,
        )

    def tour_data(self):
        return {
            "title": "Tour Đà Lạt",
            "description": "Khám phá thiên nhiên",
            "duration_days": 3,
            "duration_nights": 2,
            "base_price": 2500000,
            "image_url": None,
        }

    def test_register_name_control(self):
        self.assert_invalid_field(
            RegisterRequest,
            {
                "full_name": "Nguyễn\x00An",
                "email": "test@example.com",
                "password": "ExampleTest2026!",
            },
            "full_name",
        )

    def test_login_email_control(self):
        self.assert_invalid_field(
            LoginRequest,
            {
                "email": "test@example.com\n",
                "password": "ExampleTest2026!",
            },
            "email",
        )

    def test_password_preserved(self):
        password = "  ExampleTest2026!  "

        model = LoginRequest(
            email="test@example.com",
            password=password,
        )

        self.assertEqual(
            model.password,
            password,
        )

    def test_profile_phone_control(self):
        self.assert_invalid_field(
            ProfileUpdate,
            {
                "full_name": "Nguyễn Văn An",
                "phone": "090\n1234567",
            },
            "phone",
        )

    def test_passenger_name_control(self):
        self.assert_invalid_field(
            PassengerCreate,
            {
                "full_name": "Nguyễn\x00An",
            },
            "full_name",
        )

    def test_guide_name_control(self):
        self.assert_invalid_field(
            GuideCreate,
            {
                "full_name": "Nguyễn\x1bAn",
            },
            "full_name",
        )

    def test_tour_title_control(self):
        data = self.tour_data()
        data["title"] = "Tour\x00Đà Lạt"

        self.assert_invalid_field(
            TourCreate,
            data,
            "title",
        )

    def test_tour_description_control(self):
        data = self.tour_data()
        data["description"] = "Nội dung\x1b"

        self.assert_invalid_field(
            TourCreate,
            data,
            "description",
        )

    def test_tour_image_url_control(self):
        data = self.tour_data()
        data["image_url"] = (
            "https://example.com/image.jpg\n"
        )

        self.assert_invalid_field(
            TourCreate,
            data,
            "image_url",
        )

    def test_tour_plain_text_preserved(self):
        data = self.tour_data()
        value = "<b>Đà Lạt</b> & thiên nhiên"
        data["description"] = value

        model = TourCreate.model_validate(data)

        self.assertEqual(
            model.description,
            value,
        )

    def test_destination_name_control(self):
        self.assert_invalid_field(
            DestinationCreate,
            {
                "name": "Địa điểm\x00",
                "province": "Lâm Đồng",
            },
            "name",
        )

    def test_destination_url_control(self):
        self.assert_invalid_field(
            DestinationCreate,
            {
                "name": "Hồ Xuân Hương",
                "province": "Lâm Đồng",
                "image_url": (
                    "https://example.com/image.jpg\n"
                ),
            },
            "image_url",
        )

    def test_review_comment_control(self):
        self.assert_invalid_field(
            ReviewCreate,
            {
                "tour_id": 1,
                "rating": 5,
                "comment": "Tour rất đẹp\x1b",
            },
            "comment",
        )

    def test_review_plain_text_preserved(self):
        value = "<b>Tour rất đẹp</b>"

        model = ReviewCreate(
            tour_id=1,
            rating=5,
            comment=value,
        )

        self.assertEqual(
            model.comment,
            value,
        )

    def test_payment_transaction_control(self):
        self.assert_invalid_field(
            PaymentConfirm,
            {
                "transaction_code": "TX\n001",
            },
            "transaction_code",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
