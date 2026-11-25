
import unittest

from decimal import Decimal

from fastapi import HTTPException

from app.core.money_validation import (
    validate_money_amount,
    calculate_booking_total,
    validate_booking_amount,
)

from app.core.search_validation import (
    validate_price_range,
)


D = Decimal


# ==========================================
# 1. MONEY VALIDATION
# ==========================================

class TestMoneyValidation(unittest.TestCase):

    def test_normal_amount(self):
        self.assertEqual(
            validate_money_amount(D("2500000")),
            D("2500000.00"),
        )

    def test_minimum_amount(self):
        self.assertEqual(
            validate_money_amount(D("0.01")),
            D("0.01"),
        )

    def test_maximum_amount(self):
        self.assertEqual(
            validate_money_amount(
                D("9999999999.99")
            ),
            D("9999999999.99"),
        )

    def test_overflow_amount(self):
        with self.assertRaises(ValueError):
            validate_money_amount(
                D("10000000000")
            )

    def test_negative_amount(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("-100"))

    def test_zero_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("0"))

    def test_zero_allowed(self):
        self.assertEqual(
            validate_money_amount(
                D("0"),
                allow_zero=True,
            ),
            D("0.00"),
        )

    def test_nan(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("NaN"))

    def test_signaling_nan(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("sNaN"))

    def test_positive_infinity(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("Infinity"))

    def test_negative_infinity(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("-Infinity"))

    def test_three_decimal_places(self):
        with self.assertRaises(ValueError):
            validate_money_amount(D("100.123"))

    def test_trailing_zeros(self):
        result = validate_money_amount(
            D("100.1200")
        )

        self.assertEqual(result, D("100.12"))
        self.assertEqual(
            result.as_tuple().exponent,
            -2,
        )

    def test_normalized_exponent(self):
        result = validate_money_amount(
            D("100")
        )

        self.assertEqual(
            result.as_tuple().exponent,
            -2,
        )

    def test_extreme_zero_exponent(self):
        result = validate_money_amount(
            D("0E-1000000"),
            allow_zero=True,
        )

        self.assertEqual(str(result), "0.00")

    def test_tiny_nonzero_amount(self):
        with self.assertRaises(ValueError):
            validate_money_amount(
                D("1E-1000000")
            )

    def test_large_exponent(self):
        with self.assertRaises(ValueError):
            validate_money_amount(
                D("1E+1000000")
            )

    def test_float_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount(100.5)

    def test_integer_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount(100)

    def test_string_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount("100")

    def test_boolean_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount(True)

    def test_none_rejected(self):
        with self.assertRaises(ValueError):
            validate_money_amount(None)


# ==========================================
# 2. BOOKING TOTAL VALIDATION
# ==========================================

class TestBookingTotal(unittest.TestCase):

    def test_normal_booking(self):
        self.assertEqual(
            calculate_booking_total(
                D("2500000"), 3
            ),
            D("7500000.00"),
        )

    def test_one_passenger(self):
        self.assertEqual(
            calculate_booking_total(
                D("1000000"), 1
            ),
            D("1000000.00"),
        )

    def test_maximum_passengers(self):
        self.assertEqual(
            calculate_booking_total(
                D("1000000"), 100
            ),
            D("100000000.00"),
        )

    def test_maximum_total(self):
        self.assertEqual(
            calculate_booking_total(
                D("9999999999.99"), 1
            ),
            D("9999999999.99"),
        )

    def test_total_below_limit(self):
        self.assertEqual(
            calculate_booking_total(
                D("4999999999.99"), 2
            ),
            D("9999999999.98"),
        )

    def test_total_above_limit(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("5000000000"), 2
            )

    def test_decimal_calculation(self):
        self.assertEqual(
            calculate_booking_total(
                D("0.10"), 3
            ),
            D("0.30"),
        )

    def test_invalid_unit_price(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("-100"), 2
            )

    def test_zero_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), 0
            )

    def test_negative_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), -1
            )

    def test_too_many_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), 101
            )

    def test_float_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), 2.5
            )

    def test_string_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), "2"
            )

    def test_boolean_passengers(self):
        with self.assertRaises(ValueError):
            calculate_booking_total(
                D("100"), True
            )


# ==========================================
# 3. BOOKING AMOUNT CONSISTENCY
# ==========================================

class TestBookingAmount(unittest.TestCase):

    def test_valid_booking(self):
        self.assertEqual(
            validate_booking_amount(
                D("2500000"),
                3,
                D("7500000"),
            ),
            D("7500000.00"),
        )

    def test_maximum_amount(self):
        self.assertEqual(
            validate_booking_amount(
                D("9999999999.99"),
                1,
                D("9999999999.99"),
            ),
            D("9999999999.99"),
        )

    def test_decimal_consistency(self):
        self.assertEqual(
            validate_booking_amount(
                D("100.25"),
                3,
                D("300.75"),
            ),
            D("300.75"),
        )

    def test_total_too_low(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("299.99")
            )

    def test_total_too_high(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("300.01")
            )

    def test_zero_total(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("0")
            )

    def test_negative_total(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("-300")
            )

    def test_stored_total_overflow(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("6000000000"),
                2,
                D("12000000000"),
            )

    def test_calculated_total_overflow(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("6000000000"),
                2,
                D("9999999999.99"),
            )

    def test_invalid_precision(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("300.001")
            )

    def test_nan_total(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, D("NaN")
            )

    def test_invalid_total_type(self):
        with self.assertRaises(ValueError):
            validate_booking_amount(
                D("100"), 3, "300"
            )


# ==========================================
# 4. DECIMAL SEARCH VALIDATION
# ==========================================

class TestDecimalSearch(unittest.TestCase):

    def assert_http_error(
        self,
        min_price,
        max_price,
        expected_status,
    ):
        with self.assertRaises(
            HTTPException
        ) as context:

            validate_price_range(
                min_price,
                max_price,
            )

        self.assertEqual(
            context.exception.status_code,
            expected_status,
        )

    def test_no_filters(self):
        self.assertEqual(
            validate_price_range(None, None),
            (None, None),
        )

    def test_minimum_only(self):
        self.assertEqual(
            validate_price_range(
                D("100"), None
            ),
            (D("100.00"), None),
        )

    def test_maximum_only(self):
        self.assertEqual(
            validate_price_range(
                None, D("500")
            ),
            (None, D("500.00")),
        )

    def test_valid_range(self):
        self.assertEqual(
            validate_price_range(
                D("100"), D("500")
            ),
            (D("100.00"), D("500.00")),
        )

    def test_equal_prices(self):
        self.assertEqual(
            validate_price_range(
                D("100"), D("100")
            ),
            (D("100.00"), D("100.00")),
        )

    def test_zero_prices(self):
        self.assertEqual(
            validate_price_range(
                D("0"), D("0")
            ),
            (D("0.00"), D("0.00")),
        )

    def test_maximum_price(self):
        self.assertEqual(
            validate_price_range(
                D("0"), D("9999999999.99")
            ),
            (D("0.00"), D("9999999999.99")),
        )

    def test_reversed_range(self):
        self.assert_http_error(
            D("500"), D("100"), 400
        )

    def test_negative_minimum(self):
        self.assert_http_error(
            D("-1"), None, 422
        )

    def test_negative_maximum(self):
        self.assert_http_error(
            None, D("-1"), 422
        )

    def test_overflow(self):
        self.assert_http_error(
            None, D("10000000000"), 422
        )

    def test_nan(self):
        self.assert_http_error(
            D("NaN"), None, 422
        )

    def test_infinity(self):
        self.assert_http_error(
            None, D("Infinity"), 422
        )

    def test_invalid_precision(self):
        self.assert_http_error(
            D("100.123"), None, 422
        )

    def test_normalized_precision(self):
        min_price, max_price = (
            validate_price_range(
                D("100.1200"),
                D("500"),
            )
        )

        self.assertEqual(
            str(min_price), "100.12"
        )

        self.assertEqual(
            str(max_price), "500.00"
        )

    def test_extreme_zero_exponent(self):
        min_price, _ = validate_price_range(
            D("0E-1000000"),
            None,
        )

        self.assertEqual(
            str(min_price), "0.00"
        )


if __name__ == "__main__":
    unittest.main()
