
import unittest
from decimal import Decimal

from fastapi import HTTPException

from app.core.validation import (
    MAX_SEARCH_LENGTH,
    MAX_USER_SEARCH_LENGTH,
    MAX_PROVINCE_LENGTH,
    MAX_PAGE_SIZE,
    MAX_PAGE_NUMBER,
    MAX_PAGINATION_OFFSET,
    MAX_TOUR_PRICE,
)

from app.core.search_validation import (
    normalize_search_keyword,
    validate_price_range,
    validate_pagination,
    calculate_total_pages,
)


# ==================================================
# BASE TEST
# ==================================================

class SearchValidationTestCase(unittest.TestCase):

    def assert_http_error(
        self,
        expected_status,
        function,
        *args,
        **kwargs
    ):
        with self.assertRaises(HTTPException) as context:
            function(*args, **kwargs)

        self.assertEqual(
            context.exception.status_code,
            expected_status
        )


# ==================================================
# 1. SEARCH NORMALIZATION
# ==================================================

class TestSearchNormalization(SearchValidationTestCase):

    def test_none_keyword(self):
        self.assertIsNone(
            normalize_search_keyword(None)
        )

    def test_empty_keyword(self):
        self.assertIsNone(
            normalize_search_keyword("")
        )

    def test_blank_keyword(self):
        self.assertIsNone(
            normalize_search_keyword("   \t\r\n  ")
        )

    def test_trim_keyword(self):
        self.assertEqual(
            normalize_search_keyword("  Đà Lạt  "),
            "Đà Lạt"
        )

    def test_multiple_spaces(self):
        self.assertEqual(
            normalize_search_keyword("Tour   Đà   Lạt"),
            "Tour Đà Lạt"
        )

    def test_tab_and_newline(self):
        self.assertEqual(
            normalize_search_keyword("Tour\tĐà\nLạt"),
            "Tour Đà Lạt"
        )

    def test_unicode_nfc(self):
        self.assertEqual(
            normalize_search_keyword("Cafe\u0301"),
            "Caf\u00e9"
        )

    def test_preserve_percent(self):
        self.assertEqual(
            normalize_search_keyword("Tour 100%"),
            "Tour 100%"
        )

    def test_preserve_underscore(self):
        self.assertEqual(
            normalize_search_keyword("Tour_01"),
            "Tour_01"
        )

    def test_preserve_apostrophe(self):
        self.assertEqual(
            normalize_search_keyword("O'Brien"),
            "O'Brien"
        )

    def test_preserve_emoji(self):
        self.assertEqual(
            normalize_search_keyword("Tour 🌴"),
            "Tour 🌴"
        )

    def test_invalid_integer(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            12345
        )

    def test_invalid_boolean(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            True
        )

    def test_null_character(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "Tour\x00"
        )

    def test_delete_character(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "Tour\x7f"
        )

    def test_c1_control_character(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "Tour\x85"
        )

    def test_max_tour_search_length(self):
        keyword = "A" * MAX_SEARCH_LENGTH

        self.assertEqual(
            normalize_search_keyword(keyword),
            keyword
        )

    def test_tour_search_too_long(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "A" * (MAX_SEARCH_LENGTH + 1)
        )

    def test_max_user_search_length(self):
        keyword = "A" * MAX_USER_SEARCH_LENGTH

        self.assertEqual(
            normalize_search_keyword(
                keyword,
                MAX_USER_SEARCH_LENGTH
            ),
            keyword
        )

    def test_user_search_too_long(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "A" * (MAX_USER_SEARCH_LENGTH + 1),
            MAX_USER_SEARCH_LENGTH
        )

    def test_province_search_too_long(self):
        self.assert_http_error(
            422,
            normalize_search_keyword,
            "A" * (MAX_PROVINCE_LENGTH + 1),
            MAX_PROVINCE_LENGTH
        )

    def test_normalization_idempotence(self):
        keyword = normalize_search_keyword(
            "  Cafe\u0301   Đà Lạt  "
        )

        self.assertEqual(
            normalize_search_keyword(keyword),
            keyword
        )


# ==================================================
# 2. PRICE RANGE VALIDATION
# ==================================================

class TestPriceRangeValidation(SearchValidationTestCase):

    def test_no_price_filter(self):
        self.assertIsNone(
            validate_price_range(None, None)
        )

    def test_minimum_price_only(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("1000000"),
                None
            )
        )

    def test_maximum_price_only(self):
        self.assertIsNone(
            validate_price_range(
                None,
                Decimal("5000000")
            )
        )

    def test_valid_price_range(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("1000000"),
                Decimal("5000000")
            )
        )

    def test_equal_prices(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("1000000"),
                Decimal("1000000")
            )
        )

    def test_zero_price(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("0"),
                Decimal("0")
            )
        )

    def test_maximum_allowed_price(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("0"),
                MAX_TOUR_PRICE
            )
        )

    def test_reversed_price_range(self):
        self.assert_http_error(
            400,
            validate_price_range,
            Decimal("5000000"),
            Decimal("1000000")
        )

    def test_negative_minimum_price(self):
        self.assert_http_error(
            422,
            validate_price_range,
            Decimal("-1"),
            None
        )

    def test_negative_maximum_price(self):
        self.assert_http_error(
            422,
            validate_price_range,
            None,
            Decimal("-1")
        )

    def test_price_overflow(self):
        self.assert_http_error(
            422,
            validate_price_range,
            None,
            MAX_TOUR_PRICE + Decimal("0.01")
        )

    def test_two_decimal_places(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("100.12"),
                None
            )
        )

    def test_trailing_decimal_zeros(self):
        self.assertIsNone(
            validate_price_range(
                Decimal("100.1200"),
                None
            )
        )

    def test_invalid_decimal_places(self):
        self.assert_http_error(
            422,
            validate_price_range,
            Decimal("100.123"),
            None
        )

    def test_nan_price(self):
        self.assert_http_error(
            422,
            validate_price_range,
            Decimal("NaN"),
            None
        )

    def test_positive_infinity(self):
        self.assert_http_error(
            422,
            validate_price_range,
            Decimal("Infinity"),
            None
        )

    def test_negative_infinity(self):
        self.assert_http_error(
            422,
            validate_price_range,
            Decimal("-Infinity"),
            None
        )

    def test_invalid_price_type(self):
        self.assert_http_error(
            422,
            validate_price_range,
            "1000000",
            None
        )


# ==================================================
# 3. PAGINATION VALIDATION
# ==================================================

class TestPaginationValidation(SearchValidationTestCase):

    def test_first_page(self):
        self.assertEqual(
            validate_pagination(1, 10),
            0
        )

    def test_second_page(self):
        self.assertEqual(
            validate_pagination(2, 10),
            10
        )

    def test_maximum_page_size(self):
        self.assertEqual(
            validate_pagination(1, MAX_PAGE_SIZE),
            0
        )

    def test_maximum_offset(self):
        self.assertEqual(
            validate_pagination(101, 100),
            MAX_PAGINATION_OFFSET
        )

    def test_maximum_page_number(self):
        self.assertEqual(
            validate_pagination(MAX_PAGE_NUMBER, 1),
            MAX_PAGINATION_OFFSET
        )

    def test_zero_page(self):
        self.assert_http_error(
            422, validate_pagination, 0, 10
        )

    def test_negative_page(self):
        self.assert_http_error(
            422, validate_pagination, -1, 10
        )

    def test_page_overflow(self):
        self.assert_http_error(
            422,
            validate_pagination,
            MAX_PAGE_NUMBER + 1,
            1
        )

    def test_zero_page_size(self):
        self.assert_http_error(
            422, validate_pagination, 1, 0
        )

    def test_negative_page_size(self):
        self.assert_http_error(
            422, validate_pagination, 1, -1
        )

    def test_page_size_overflow(self):
        self.assert_http_error(
            422,
            validate_pagination,
            1,
            MAX_PAGE_SIZE + 1
        )

    def test_offset_overflow(self):
        self.assert_http_error(
            422, validate_pagination, 102, 100
        )

    def test_float_page(self):
        self.assert_http_error(
            422, validate_pagination, 1.5, 10
        )

    def test_float_page_size(self):
        self.assert_http_error(
            422, validate_pagination, 1, 2.5
        )

    def test_string_page(self):
        self.assert_http_error(
            422, validate_pagination, "1", 10
        )

    def test_boolean_page(self):
        self.assert_http_error(
            422, validate_pagination, True, 10
        )

    def test_boolean_page_size(self):
        self.assert_http_error(
            422, validate_pagination, 1, True
        )


# ==================================================
# 4. TOTAL PAGES
# ==================================================

class TestTotalPages(unittest.TestCase):

    def test_empty_result(self):
        self.assertEqual(
            calculate_total_pages(0, 10),
            0
        )

    def test_single_result(self):
        self.assertEqual(
            calculate_total_pages(1, 10),
            1
        )

    def test_exact_division(self):
        self.assertEqual(
            calculate_total_pages(100, 10),
            10
        )

    def test_partial_last_page(self):
        self.assertEqual(
            calculate_total_pages(105, 20),
            6
        )

    def test_page_size_one(self):
        self.assertEqual(
            calculate_total_pages(25, 1),
            25
        )

    def test_large_total(self):
        self.assertEqual(
            calculate_total_pages(1000000, 100),
            10000
        )

    def test_negative_total(self):
        with self.assertRaises(ValueError):
            calculate_total_pages(-1, 10)

    def test_invalid_total_type(self):
        with self.assertRaises(ValueError):
            calculate_total_pages("100", 10)

    def test_zero_page_size(self):
        with self.assertRaises(ValueError):
            calculate_total_pages(100, 0)

    def test_page_size_overflow(self):
        with self.assertRaises(ValueError):
            calculate_total_pages(100, 101)


if __name__ == "__main__":
    unittest.main(verbosity=2)
