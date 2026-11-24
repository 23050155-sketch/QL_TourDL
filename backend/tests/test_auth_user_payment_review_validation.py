
import unittest

from pydantic import ValidationError

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
)

from app.schemas.user import (
    ProfileUpdate,
    ChangePasswordRequest,
    UserStatusUpdate,
)

from app.schemas.payment import (
    PaymentCreate,
    PaymentConfirm,
)

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewPublicResponse,
)

from app.core.validation import (
    MAX_UNSIGNED_BIGINT,
    MAX_TRANSACTION_CODE_LENGTH,
    MAX_REVIEW_COMMENT_LENGTH,
)


# Email đúng cấu trúc nhưng vượt 190 ký tự
LONG_EMAIL = (
    "a" * 60
    + "@"
    + "b" * 60
    + "."
    + "c" * 60
    + "."
    + "d" * 20
    + ".com"
)


class TestAuthValidation(unittest.TestCase):

    def valid_register(self):
        return {
            "full_name": "Nguyen Van Test",
            "email": "customer@example.com",
            "password": "TestPassword123!",
            "phone": "0900000000",
        }

    def assert_invalid(self, **changes):
        data = self.valid_register()
        data.update(changes)

        with self.assertRaises(ValidationError):
            RegisterRequest(**data)

    # 1. Đăng ký hợp lệ
    def test_valid_register(self):
        user = RegisterRequest(**self.valid_register())

        self.assertEqual(
            user.email,
            "customer@example.com"
        )

    # 2. Chuẩn hóa họ tên
    def test_normalize_full_name(self):
        data = self.valid_register()
        data["full_name"] = "  Nguyen Van Test  "

        user = RegisterRequest(**data)

        self.assertEqual(
            user.full_name,
            "Nguyen Van Test"
        )

    # 3. Họ tên chỉ có khoảng trắng
    def test_blank_full_name(self):
        self.assert_invalid(full_name="     ")

    # 4. Họ tên vượt giới hạn
    def test_long_full_name(self):
        self.assert_invalid(full_name="A" * 151)

    # 5. Email sai định dạng
    def test_invalid_email(self):
        self.assert_invalid(email="invalid-email")

    # 6. Email đăng ký quá dài
    def test_long_register_email(self):
        self.assert_invalid(email=LONG_EMAIL)

    # 7. Mật khẩu quá ngắn
    def test_short_password(self):
        self.assert_invalid(password="1234567")

    # 8. Mật khẩu quá dài
    def test_long_password(self):
        self.assert_invalid(password="A" * 129)

    # 9. Số điện thoại quá dài
    def test_long_phone(self):
        self.assert_invalid(phone="0" * 21)

    # 10. Không cho phép tự đăng ký role
    def test_extra_role(self):
        self.assert_invalid(role="admin")

    # 11. Đăng nhập hợp lệ
    def test_valid_login(self):
        login = LoginRequest(
            email="customer@example.com",
            password="TestPassword123!"
        )

        self.assertEqual(
            login.email,
            "customer@example.com"
        )

    # 12. Email đăng nhập quá dài
    def test_long_login_email(self):
        with self.assertRaises(ValidationError):
            LoginRequest(
                email=LONG_EMAIL,
                password="TestPassword123!"
            )

    # 13. Mật khẩu đăng nhập rỗng
    def test_empty_login_password(self):
        with self.assertRaises(ValidationError):
            LoginRequest(
                email="customer@example.com",
                password=""
            )

    # 14. Không thay đổi mật khẩu
    def test_password_preserved(self):
        password = "  TestPassword123!  "

        login = LoginRequest(
            email="customer@example.com",
            password=password
        )

        self.assertEqual(login.password, password)

    # 15. Response không chứa thông tin bảo mật
    def test_user_response_privacy(self):
        fields = UserResponse.model_fields

        self.assertNotIn("password", fields)
        self.assertNotIn("password_hash", fields)
        self.assertNotIn("token_version", fields)


class TestUserValidation(unittest.TestCase):

    # 16. Cập nhật Profile hợp lệ
    def test_valid_profile(self):
        profile = ProfileUpdate(
            full_name="Nguyen Van Test",
            phone="0900000000"
        )

        self.assertEqual(
            profile.full_name,
            "Nguyen Van Test"
        )

    # 17. Chuẩn hóa Profile
    def test_profile_whitespace(self):
        profile = ProfileUpdate(
            full_name="  Nguyen Van Test  ",
            phone="  0900000000  "
        )

        self.assertEqual(
            profile.full_name,
            "Nguyen Van Test"
        )

        self.assertEqual(
            profile.phone,
            "0900000000"
        )

    # 18. Họ tên null
    def test_null_full_name(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(full_name=None)

    # 19. Không cho phép tự cập nhật role
    def test_profile_extra_role(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(
                full_name="Nguyen Van Test",
                role="admin"
            )

    # 20. Request đổi mật khẩu hợp lệ
    def test_valid_change_password(self):
        data = ChangePasswordRequest(
            current_password="OldPassword123!",
            new_password="NewPassword123!",
            confirm_password="NewPassword123!"
        )

        self.assertEqual(
            data.new_password,
            data.confirm_password
        )

    # 21. Mật khẩu mới quá ngắn
    def test_short_new_password(self):
        with self.assertRaises(ValidationError):
            ChangePasswordRequest(
                current_password="OldPassword123!",
                new_password="123",
                confirm_password="123"
            )

    # 22. Giữ nguyên khoảng trắng mật khẩu
    def test_password_whitespace(self):
        password = "  NewPassword123!  "

        data = ChangePasswordRequest(
            current_password="OldPassword123!",
            new_password=password,
            confirm_password=password
        )

        self.assertEqual(data.new_password, password)

    # 23. Trạng thái hợp lệ
    def test_valid_status(self):
        user = UserStatusUpdate(status="inactive")

        self.assertEqual(user.status, "inactive")

    # 24. Trạng thái không hợp lệ
    def test_invalid_status(self):
        with self.assertRaises(ValidationError):
            UserStatusUpdate(status="unknown")


class TestPaymentValidation(unittest.TestCase):

    def assert_invalid(self, **changes):
        data = {
            "booking_id": 1,
            "payment_method": "bank_transfer",
        }

        data.update(changes)

        with self.assertRaises(ValidationError):
            PaymentCreate(**data)

    # 25. Phương thức thanh toán hợp lệ
    def test_valid_payment_methods(self):
        methods = [
            "cash",
            "bank_transfer",
            "online",
        ]

        for method in methods:
            with self.subTest(method=method):
                payment = PaymentCreate(
                    booking_id=1,
                    payment_method=method
                )

                self.assertEqual(
                    payment.payment_method,
                    method
                )

    # 26. ID bằng 0
    def test_zero_booking_id(self):
        self.assert_invalid(booking_id=0)

    # 27. ID âm
    def test_negative_booking_id(self):
        self.assert_invalid(booking_id=-1)

    # 28. ID vượt giới hạn
    def test_booking_id_overflow(self):
        self.assert_invalid(
            booking_id=MAX_UNSIGNED_BIGINT + 1
        )

    # 29. ID dạng chuỗi
    def test_string_booking_id(self):
        self.assert_invalid(booking_id="1")

    # 30. ID dạng boolean
    def test_boolean_booking_id(self):
        self.assert_invalid(booking_id=True)

    # 31. ID dạng số thực
    def test_float_booking_id(self):
        self.assert_invalid(booking_id=1.5)

    # 32. Phương thức thanh toán sai
    def test_invalid_payment_method(self):
        self.assert_invalid(
            payment_method="unknown"
        )

    # 33. Không cho phép gửi số tiền
    def test_extra_amount(self):
        self.assert_invalid(amount=1000)

    # 34. Không cho phép gửi trạng thái
    def test_extra_status(self):
        self.assert_invalid(status="success")

    # 35. Mã giao dịch hợp lệ
    def test_valid_transaction_code(self):
        payment = PaymentConfirm(
            transaction_code="TEST-001"
        )

        self.assertEqual(
            payment.transaction_code,
            "TEST-001"
        )

    # 36. Mã giao dịch vượt giới hạn
    def test_long_transaction_code(self):
        with self.assertRaises(ValidationError):
            PaymentConfirm(
                transaction_code=(
                    "A" * (
                        MAX_TRANSACTION_CODE_LENGTH + 1
                    )
                )
            )

    # 37. Mã giao dịch không bắt buộc
    def test_optional_transaction_code(self):
        payment = PaymentConfirm()

        self.assertIsNone(
            payment.transaction_code
        )

    # 38. Không cho phép thay đổi số tiền
    def test_confirm_extra_amount(self):
        with self.assertRaises(ValidationError):
            PaymentConfirm(amount=1000)


class TestReviewValidation(unittest.TestCase):

    def assert_invalid(self, **changes):
        data = {
            "tour_id": 1,
            "rating": 5,
            "comment": "Tour kiem thu",
        }

        data.update(changes)

        with self.assertRaises(ValidationError):
            ReviewCreate(**data)

    # 39. Đánh giá hợp lệ
    def test_valid_rating(self):
        for rating in range(1, 6):
            with self.subTest(rating=rating):
                review = ReviewCreate(
                    tour_id=1,
                    rating=rating
                )

                self.assertEqual(
                    review.rating,
                    rating
                )

    # 40. ID Tour bằng 0
    def test_zero_tour_id(self):
        self.assert_invalid(tour_id=0)

    # 41. ID Tour vượt giới hạn
    def test_tour_id_overflow(self):
        self.assert_invalid(
            tour_id=MAX_UNSIGNED_BIGINT + 1
        )

    # 42. ID Tour dạng chuỗi
    def test_string_tour_id(self):
        self.assert_invalid(tour_id="1")

    # 43. Rating bằng 0
    def test_zero_rating(self):
        self.assert_invalid(rating=0)

    # 44. Rating lớn hơn 5
    def test_rating_overflow(self):
        self.assert_invalid(rating=6)

    # 45. Rating dạng chuỗi
    def test_string_rating(self):
        self.assert_invalid(rating="5")

    # 46. Rating dạng boolean
    def test_boolean_rating(self):
        self.assert_invalid(rating=True)

    # 47. Rating dạng số thực
    def test_float_rating(self):
        self.assert_invalid(rating=4.5)

    # 48. Bình luận quá dài
    def test_long_comment(self):
        self.assert_invalid(
            comment=(
                "A" * (
                    MAX_REVIEW_COMMENT_LENGTH + 1
                )
            )
        )

    # 49. Không cho phép giả mạo user_id
    def test_extra_user_id(self):
        self.assert_invalid(user_id=2)

    # 50. Cập nhật rating hợp lệ
    def test_valid_update_rating(self):
        review = ReviewUpdate(rating=4)

        self.assertEqual(review.rating, 4)

    # 51. Không cho phép rating null
    def test_null_rating(self):
        with self.assertRaises(ValidationError):
            ReviewUpdate(rating=None)

    # 52. Chỉ cập nhật bình luận
    def test_comment_only_update(self):
        review = ReviewUpdate(
            comment="Noi dung moi"
        )

        self.assertEqual(
            review.model_dump(exclude_unset=True),
            {"comment": "Noi dung moi"}
        )

    # 53. Cho phép xóa bình luận
    def test_null_comment(self):
        review = ReviewUpdate(comment=None)

        self.assertEqual(
            review.model_dump(exclude_unset=True),
            {"comment": None}
        )

    # 54. Response công khai không có user_id
    def test_public_response_privacy(self):
        review = ReviewPublicResponse(
            id=1,
            tour_id=1,
            user_id=2,
            rating=5
        )

        self.assertNotIn(
            "user_id",
            review.model_dump()
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
