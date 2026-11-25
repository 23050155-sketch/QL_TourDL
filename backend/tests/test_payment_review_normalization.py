
import unittest

from pydantic import ValidationError

from app.schemas.payment import (
    PaymentCreate,
    PaymentConfirm,
    PaymentResponse,
)

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewPublicResponse,
)


class TestPaymentNormalization(unittest.TestCase):

    # 1. Loại bỏ khoảng trắng đầu cuối
    def test_transaction_trim(self):
        payment = PaymentConfirm(
            transaction_code="  TX-001  "
        )

        self.assertEqual(
            payment.transaction_code,
            "TX-001"
        )

    # 2. Giữ nguyên chữ hoa và chữ thường
    def test_transaction_case(self):
        payment = PaymentConfirm(
            transaction_code="  TX-AbC-001  "
        )

        self.assertEqual(
            payment.transaction_code,
            "TX-AbC-001"
        )

    # 3. Giữ nguyên số 0 đầu chuỗi
    def test_transaction_leading_zeros(self):
        payment = PaymentConfirm(
            transaction_code="000123456"
        )

        self.assertEqual(
            payment.transaction_code,
            "000123456"
        )

    # 4. Giữ nguyên khoảng trắng bên trong
    def test_transaction_internal_spaces(self):
        payment = PaymentConfirm(
            transaction_code="  TX  001  "
        )

        self.assertEqual(
            payment.transaction_code,
            "TX  001"
        )

    # 5. Giữ nguyên Unicode của mã giao dịch
    def test_transaction_unicode_preserved(self):
        value = "TX-e\u0301"

        payment = PaymentConfirm(
            transaction_code=value
        )

        self.assertEqual(
            payment.transaction_code,
            value
        )

    # 6. Mã giao dịch rỗng
    def test_empty_transaction(self):
        payment = PaymentConfirm(
            transaction_code=""
        )

        self.assertIsNone(
            payment.transaction_code
        )

    # 7. Mã giao dịch chỉ có khoảng trắng
    def test_blank_transaction(self):
        payment = PaymentConfirm(
            transaction_code="   "
        )

        self.assertIsNone(
            payment.transaction_code
        )

    # 8. Mã giao dịch null
    def test_null_transaction(self):
        payment = PaymentConfirm(
            transaction_code=None
        )

        self.assertIsNone(
            payment.transaction_code
        )

    # 9. Không gửi mã giao dịch
    def test_missing_transaction(self):
        payment = PaymentConfirm()

        self.assertIsNone(
            payment.transaction_code
        )

    # 10. Giới hạn đúng 150 ký tự
    def test_transaction_max_length(self):
        value = "A" * 150

        payment = PaymentConfirm(
            transaction_code="  " + value + "  "
        )

        self.assertEqual(
            payment.transaction_code,
            value
        )

    # 11. Mã giao dịch quá dài
    def test_transaction_too_long(self):
        with self.assertRaises(ValidationError):
            PaymentConfirm(
                transaction_code="A" * 151
            )

    # 12. Mã giao dịch sai kiểu dữ liệu
    def test_transaction_invalid_type(self):
        with self.assertRaises(ValidationError):
            PaymentConfirm(
                transaction_code=123456
            )

    # 13. Không cho phép gửi số tiền khi xác nhận
    def test_payment_confirm_extra_field(self):
        with self.assertRaises(ValidationError):
            PaymentConfirm(
                transaction_code="TX-001",
                amount=1000
            )

    # 14. Giữ nguyên kiểm tra phương thức thanh toán
    def test_invalid_payment_method(self):
        with self.assertRaises(ValidationError):
            PaymentCreate(
                booking_id=1,
                payment_method="invalid"
            )

    # 15. Không cho phép gửi số tiền khi tạo Payment
    def test_payment_create_extra_amount(self):
        with self.assertRaises(ValidationError):
            PaymentCreate(
                booking_id=1,
                payment_method="cash",
                amount=1000
            )

    # 16. Response giữ nguyên dữ liệu cũ
    def test_payment_response_compatibility(self):
        payment = PaymentResponse(
            id=1,
            booking_id=1,
            amount="2500000.00",
            payment_method="cash",
            status="success",
            transaction_code="  TX-OLD-001  "
        )

        self.assertEqual(
            payment.transaction_code,
            "  TX-OLD-001  "
        )


class TestReviewNormalization(unittest.TestCase):

    def create_review(self, **changes):
        data = {
            "tour_id": 1,
            "rating": 5,
            "comment": "Good tour",
        }

        data.update(changes)

        return ReviewCreate(**data)

    # 17. Chuẩn hóa khoảng trắng đầu cuối
    def test_comment_trim(self):
        review = self.create_review(
            comment="  Good tour  "
        )

        self.assertEqual(
            review.comment,
            "Good tour"
        )

    # 18. Chuẩn hóa Unicode NFC
    def test_comment_unicode(self):
        review = self.create_review(
            comment="Cafe\u0301"
        )

        self.assertEqual(
            review.comment,
            "Caf\u00e9"
        )

    # 19. Chuẩn hóa CRLF
    def test_comment_crlf(self):
        review = self.create_review(
            comment="Line 1  \r\nLine 2  "
        )

        self.assertEqual(
            review.comment,
            "Line 1\nLine 2"
        )

    # 20. Chuẩn hóa CR
    def test_comment_cr(self):
        review = self.create_review(
            comment="Line 1\rLine 2"
        )

        self.assertEqual(
            review.comment,
            "Line 1\nLine 2"
        )

    # 21. Giữ nguyên dòng trống
    def test_comment_blank_lines(self):
        review = self.create_review(
            comment="Line 1\n\nLine 2"
        )

        self.assertEqual(
            review.comment,
            "Line 1\n\nLine 2"
        )

    # 22. Giữ nguyên khoảng trắng bên trong
    def test_comment_internal_spaces(self):
        review = self.create_review(
            comment="Very   good tour"
        )

        self.assertEqual(
            review.comment,
            "Very   good tour"
        )

    # 23. Bình luận rỗng
    def test_empty_comment(self):
        review = self.create_review(
            comment=""
        )

        self.assertIsNone(review.comment)

    # 24. Bình luận chỉ có khoảng trắng
    def test_blank_comment(self):
        review = self.create_review(
            comment="  \r\n  "
        )

        self.assertIsNone(review.comment)

    # 25. Bình luận null
    def test_null_comment(self):
        review = self.create_review(
            comment=None
        )

        self.assertIsNone(review.comment)

    # 26. Không gửi bình luận
    def test_missing_comment(self):
        review = ReviewCreate(
            tour_id=1,
            rating=5
        )

        self.assertIsNone(review.comment)

    # 27. Giới hạn đúng 2000 ký tự
    def test_comment_max_length(self):
        value = "A" * 2000

        review = self.create_review(
            comment="  " + value + "  "
        )

        self.assertEqual(
            review.comment,
            value
        )

    # 28. Bình luận quá dài
    def test_comment_too_long(self):
        with self.assertRaises(ValidationError):
            self.create_review(
                comment="A" * 2001
            )

    # 29. Bình luận sai kiểu dữ liệu
    def test_comment_invalid_type(self):
        with self.assertRaises(ValidationError):
            self.create_review(
                comment=12345
            )

    # 30. Chuẩn hóa bình luận khi cập nhật
    def test_review_update_normalization(self):
        review = ReviewUpdate(
            comment="  Updated comment  \r\nLine 2  "
        )

        self.assertEqual(
            review.comment,
            "Updated comment\nLine 2"
        )

    # 31. Xóa bình luận bằng chuỗi rỗng
    def test_clear_comment_with_blank(self):
        review = ReviewUpdate(
            comment="   "
        )

        self.assertEqual(
            review.model_dump(exclude_unset=True),
            {"comment": None}
        )

    # 32. Xóa bình luận bằng null
    def test_clear_comment_with_null(self):
        review = ReviewUpdate(
            comment=None
        )

        self.assertEqual(
            review.model_dump(exclude_unset=True),
            {"comment": None}
        )

    # 33. Không ghi đè bình luận nếu không gửi
    def test_partial_rating_update(self):
        review = ReviewUpdate(
            rating=4
        )

        self.assertEqual(
            review.model_dump(exclude_unset=True),
            {"rating": 4}
        )

    # 34. Không cho phép rating null
    def test_null_rating(self):
        with self.assertRaises(ValidationError):
            ReviewUpdate(rating=None)

    # 35. Không cho phép rating vượt giới hạn
    def test_invalid_rating(self):
        with self.assertRaises(ValidationError):
            self.create_review(rating=6)

    # 36. Không cho phép rating dạng chuỗi
    def test_string_rating(self):
        with self.assertRaises(ValidationError):
            self.create_review(rating="5")

    # 37. Không cho phép tự gửi user_id
    def test_review_extra_user_id(self):
        with self.assertRaises(ValidationError):
            self.create_review(user_id=99)

    # 38. Không công khai user_id
    def test_public_review_privacy(self):
        review = ReviewPublicResponse(
            id=1,
            tour_id=1,
            rating=5,
            comment="Good tour",
            user_id=99
        )

        self.assertNotIn(
            "user_id",
            review.model_dump()
        )

    # 39. Response giữ nguyên dữ liệu cũ
    def test_review_response_compatibility(self):
        review = ReviewResponse(
            id=1,
            user_id=1,
            tour_id=1,
            rating=5,
            comment="  Old comment  "
        )

        self.assertEqual(
            review.comment,
            "  Old comment  "
        )

    # 40. Giữ nguyên biểu tượng cảm xúc
    def test_comment_emoji(self):
        review = self.create_review(
            comment="  Great tour! 😊  "
        )

        self.assertEqual(
            review.comment,
            "Great tour! 😊"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
