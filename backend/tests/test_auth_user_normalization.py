
import unittest

from pydantic import ValidationError

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)

from app.schemas.user import (
    ProfileUpdate,
    ChangePasswordRequest,
)


class TestAuthNormalization(unittest.TestCase):

    def valid_register(self):
        return {
            "full_name": "Nguyen Van An",
            "email": "customer@example.com",
            "password": "TestPassword123!",
            "phone": "0901234567",
        }

    def create_register(self, **changes):
        data = self.valid_register()
        data.update(changes)

        return RegisterRequest(**data)

    # 1. Loại bỏ khoảng trắng trong họ tên
    def test_normalize_full_name(self):
        user = self.create_register(
            full_name="  Nguyen   Van   An  "
        )

        self.assertEqual(
            user.full_name,
            "Nguyen Van An"
        )

    # 2. Chuẩn hóa Unicode
    def test_normalize_unicode(self):
        user = self.create_register(
            full_name="Cafe\u0301"
        )

        self.assertEqual(
            user.full_name,
            "Caf\u00e9"
        )

    # 3. Họ tên chỉ có khoảng trắng
    def test_blank_full_name(self):
        with self.assertRaises(ValidationError):
            self.create_register(full_name="   ")

    # 4. Chuẩn hóa email đăng ký
    def test_register_email(self):
        user = self.create_register(
            email="  CUSTOMER@EXAMPLE.COM  "
        )

        self.assertEqual(
            user.email,
            "customer@example.com"
        )

    # 5. Chuẩn hóa email đăng nhập
    def test_login_email(self):
        login = LoginRequest(
            email="  CUSTOMER@EXAMPLE.COM  ",
            password="TestPassword123!"
        )

        self.assertEqual(
            login.email,
            "customer@example.com"
        )

    # 6. Email không hợp lệ
    def test_invalid_email(self):
        with self.assertRaises(ValidationError):
            self.create_register(
                email=" invalid-email "
            )

    # 7. Chuẩn hóa dấu cách trong số điện thoại
    def test_phone_spaces(self):
        user = self.create_register(
            phone="090 123 4567"
        )

        self.assertEqual(
            user.phone,
            "0901234567"
        )

    # 8. Chuẩn hóa dấu gạch ngang
    def test_phone_hyphens(self):
        user = self.create_register(
            phone="090-123-4567"
        )

        self.assertEqual(
            user.phone,
            "0901234567"
        )

    # 9. Số điện thoại quốc tế
    def test_international_phone(self):
        user = self.create_register(
            phone="+84 901 234 567"
        )

        self.assertEqual(
            user.phone,
            "+84901234567"
        )

    # 10. Số điện thoại rỗng
    def test_empty_phone(self):
        user = self.create_register(phone="")

        self.assertIsNone(user.phone)

    # 11. Số điện thoại chỉ có khoảng trắng
    def test_blank_phone(self):
        user = self.create_register(phone="   ")

        self.assertIsNone(user.phone)

    # 12. Số điện thoại null
    def test_null_phone(self):
        user = self.create_register(phone=None)

        self.assertIsNone(user.phone)

    # 13. Số điện thoại không hợp lệ
    def test_invalid_phone(self):
        invalid_values = [
            "abc123",
            "123",
            "090abc1234",
            "---",
            "++84901234567",
            "1" * 16,
            901234567,
        ]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    self.create_register(phone=value)

    # 14. Không chuẩn hóa mật khẩu đăng ký
    def test_register_password_preserved(self):
        password = "  TestPassword123!  "

        user = self.create_register(
            password=password
        )

        self.assertEqual(
            user.password,
            password
        )

    # 15. Không chuẩn hóa mật khẩu đăng nhập
    def test_login_password_preserved(self):
        password = "  TestPassword123!  "

        login = LoginRequest(
            email="customer@example.com",
            password=password
        )

        self.assertEqual(
            login.password,
            password
        )


class TestUserNormalization(unittest.TestCase):

    # 16. Chuẩn hóa họ tên Profile
    def test_profile_full_name(self):
        profile = ProfileUpdate(
            full_name="  Nguyen   Van   An  "
        )

        self.assertEqual(
            profile.full_name,
            "Nguyen Van An"
        )

    # 17. Chuẩn hóa số điện thoại Profile
    def test_profile_phone(self):
        profile = ProfileUpdate(
            full_name="Nguyen Van An",
            phone="090-123-4567"
        )

        self.assertEqual(
            profile.phone,
            "0901234567"
        )

    # 18. Chuẩn hóa số điện thoại quốc tế
    def test_profile_international_phone(self):
        profile = ProfileUpdate(
            full_name="Nguyen Van An",
            phone="+84 901 234 567"
        )

        self.assertEqual(
            profile.phone,
            "+84901234567"
        )

    # 19. Cho phép xóa số điện thoại
    def test_profile_blank_phone(self):
        profile = ProfileUpdate(
            full_name="Nguyen Van An",
            phone="   "
        )

        self.assertIsNone(profile.phone)

    # 20. Từ chối số điện thoại sai định dạng
    def test_profile_invalid_phone(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(
                full_name="Nguyen Van An",
                phone="abc123"
            )

    # 21. Từ chối họ tên rỗng
    def test_profile_blank_name(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(full_name="   ")

    # 22. Không cho phép thay đổi role
    def test_profile_extra_role(self):
        with self.assertRaises(ValidationError):
            ProfileUpdate(
                full_name="Nguyen Van An",
                role="admin"
            )

    # 23. Giữ nguyên toàn bộ mật khẩu
    def test_change_password_preserved(self):
        current = "  OldPassword123!  "
        new = "  NewPassword123!  "

        data = ChangePasswordRequest(
            current_password=current,
            new_password=new,
            confirm_password=new
        )

        self.assertEqual(
            data.current_password,
            current
        )

        self.assertEqual(
            data.new_password,
            new
        )

        self.assertEqual(
            data.confirm_password,
            new
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
