
import unittest

from app.core.normalization import (
    normalize_unicode,
    normalize_single_line,
    normalize_multiline,
    normalize_optional_text,
    normalize_optional_multiline,
    normalize_email,
    normalize_phone,
    validate_phone_format,
    normalize_optional_url,
    validate_image_url,
    normalize_transaction_code,
)


# Kiểm thử chuẩn hóa Unicode
class TestUnicodeNormalization(unittest.TestCase):

    def test_unicode_nfc(self):
        self.assertEqual(
            normalize_unicode("Cafe\u0301"),
            "Caf\u00e9"
        )

    def test_vietnamese_unicode(self):
        self.assertEqual(
            normalize_unicode("Đa\u0300 La\u0323t"),
            "Đà Lạt"
        )

    def test_unicode_none(self):
        self.assertIsNone(normalize_unicode(None))

    def test_unicode_non_string(self):
        self.assertEqual(normalize_unicode(123), 123)


# Kiểm thử văn bản một dòng
class TestSingleLineNormalization(unittest.TestCase):

    def test_trim_spaces(self):
        self.assertEqual(
            normalize_single_line("  Đà Lạt  "),
            "Đà Lạt"
        )

    def test_multiple_spaces(self):
        self.assertEqual(
            normalize_single_line("Tour   Đà   Lạt"),
            "Tour Đà Lạt"
        )

    def test_tab_and_newline(self):
        self.assertEqual(
            normalize_single_line("Tour\tĐà\nLạt"),
            "Tour Đà Lạt"
        )

    def test_blank_string(self):
        self.assertEqual(
            normalize_single_line("   "),
            ""
        )

    def test_unicode_whitespace(self):
        self.assertEqual(
            normalize_single_line("Tour\u00a0Đà Lạt"),
            "Tour Đà Lạt"
        )


# Kiểm thử văn bản nhiều dòng
class TestMultilineNormalization(unittest.TestCase):

    def test_crlf(self):
        self.assertEqual(
            normalize_multiline("Line 1\r\nLine 2"),
            "Line 1\nLine 2"
        )

    def test_cr(self):
        self.assertEqual(
            normalize_multiline("Line 1\rLine 2"),
            "Line 1\nLine 2"
        )

    def test_trailing_spaces(self):
        self.assertEqual(
            normalize_multiline("Line 1  \nLine 2  "),
            "Line 1\nLine 2"
        )

    def test_preserve_blank_lines(self):
        self.assertEqual(
            normalize_multiline("Line 1\n\nLine 2"),
            "Line 1\n\nLine 2"
        )

    def test_preserve_internal_spaces(self):
        self.assertEqual(
            normalize_multiline("Very   good tour"),
            "Very   good tour"
        )


# Kiểm thử văn bản tùy chọn
class TestOptionalNormalization(unittest.TestCase):

    def test_optional_text_blank(self):
        self.assertIsNone(
            normalize_optional_text("   ")
        )

    def test_optional_text_none(self):
        self.assertIsNone(
            normalize_optional_text(None)
        )

    def test_optional_text_valid(self):
        self.assertEqual(
            normalize_optional_text("  Đà   Lạt  "),
            "Đà Lạt"
        )

    def test_optional_multiline_blank(self):
        self.assertIsNone(
            normalize_optional_multiline(" \r\n ")
        )

    def test_optional_multiline_valid(self):
        self.assertEqual(
            normalize_optional_multiline(
                " Line 1  \r\nLine 2 "
            ),
            "Line 1\nLine 2"
        )


# Kiểm thử email
class TestEmailNormalization(unittest.TestCase):

    def test_email_lowercase(self):
        self.assertEqual(
            normalize_email("USER@EXAMPLE.COM"),
            "user@example.com"
        )

    def test_email_trim(self):
        self.assertEqual(
            normalize_email("  user@example.com  "),
            "user@example.com"
        )

    def test_email_non_string(self):
        self.assertEqual(
            normalize_email(123),
            123
        )

    def test_email_none(self):
        self.assertIsNone(normalize_email(None))


# Kiểm thử số điện thoại
class TestPhoneNormalization(unittest.TestCase):

    def test_phone_spaces(self):
        self.assertEqual(
            normalize_phone("090 123 4567"),
            "0901234567"
        )

    def test_phone_hyphens(self):
        self.assertEqual(
            normalize_phone("090-123-4567"),
            "0901234567"
        )

    def test_phone_international(self):
        self.assertEqual(
            normalize_phone("+84 (90) 123-4567"),
            "+84901234567"
        )

    def test_phone_blank(self):
        self.assertIsNone(normalize_phone("   "))

    def test_phone_none(self):
        self.assertIsNone(normalize_phone(None))

    def test_phone_valid_format(self):
        self.assertEqual(
            validate_phone_format("0901234567"),
            "0901234567"
        )

    def test_phone_invalid_letters(self):
        with self.assertRaises(ValueError):
            validate_phone_format("090ABC4567")

    def test_phone_invalid_length(self):
        for value in ["123456", "1" * 16]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_phone_format(value)

    def test_phone_invalid_type(self):
        with self.assertRaises(ValueError):
            validate_phone_format(123456789)


# Kiểm thử URL
class TestUrlNormalization(unittest.TestCase):

    def test_url_trim(self):
        self.assertEqual(
            normalize_optional_url(
                "  https://example.com/Image.JPG  "
            ),
            "https://example.com/Image.JPG"
        )

    def test_url_blank(self):
        self.assertIsNone(
            normalize_optional_url("   ")
        )

    def test_url_none(self):
        self.assertIsNone(
            normalize_optional_url(None)
        )

    def test_url_valid(self):
        for url in [
            "http://example.com/image.jpg",
            "https://example.com/image.jpg",
        ]:
            with self.subTest(url=url):
                self.assertEqual(
                    validate_image_url(url),
                    url
                )

    def test_url_invalid(self):
        for url in [
            "javascript:void(0)",
            "file:///image.jpg",
            "/images/tour.jpg",
            "https://",
        ]:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_image_url(url)


# Kiểm thử mã giao dịch
class TestTransactionNormalization(unittest.TestCase):

    def test_transaction_trim(self):
        self.assertEqual(
            normalize_transaction_code("  TX-001  "),
            "TX-001"
        )

    def test_transaction_case(self):
        self.assertEqual(
            normalize_transaction_code("TX-AbC-001"),
            "TX-AbC-001"
        )

    def test_transaction_internal_spaces(self):
        self.assertEqual(
            normalize_transaction_code("TX  001"),
            "TX  001"
        )

    def test_transaction_leading_zeros(self):
        self.assertEqual(
            normalize_transaction_code("000123"),
            "000123"
        )

    def test_transaction_blank(self):
        self.assertIsNone(
            normalize_transaction_code("   ")
        )


# Kiểm thử tính nhất quán khi chuẩn hóa nhiều lần
class TestNormalizationIdempotence(unittest.TestCase):

    def test_idempotence(self):

        cases = [
            (
                normalize_unicode,
                "Cafe\u0301"
            ),
            (
                normalize_single_line,
                "  Tour   Đà Lạt  "
            ),
            (
                normalize_multiline,
                " Line 1  \r\nLine 2 "
            ),
            (
                normalize_optional_text,
                "   "
            ),
            (
                normalize_optional_multiline,
                " \r\n "
            ),
            (
                normalize_email,
                "  USER@EXAMPLE.COM  "
            ),
            (
                normalize_phone,
                "+84 (90) 123-4567"
            ),
            (
                normalize_optional_url,
                "  https://example.com/Image.JPG  "
            ),
            (
                normalize_transaction_code,
                "  TX-AbC-001  "
            ),
        ]

        for function, value in cases:
            with self.subTest(
                function=function.__name__
            ):
                first_result = function(value)
                second_result = function(first_result)

                self.assertEqual(
                    first_result,
                    second_result
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
