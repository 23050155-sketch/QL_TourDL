
import secrets
import unittest
from datetime import datetime, timedelta, timezone

import jwt


class TestJWTClaims(unittest.TestCase):

    def setUp(self):

        # Khóa riêng chỉ dùng cho kiểm thử
        self.secret = secrets.token_hex(32)

        self.algorithm = "HS256"

        now = datetime.now(timezone.utc)

        # Payload giả lập
        self.payload = {
            "sub": "1",
            "type": "access",
            "ver": 1,
            "iat": now,
            "exp": now + timedelta(minutes=30)
        }

    # Kiểm tra JWT trong môi trường kiểm thử
    def decode_token(self, token):

        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            options={
                "require": [
                    "sub",
                    "type",
                    "ver",
                    "iat",
                    "exp"
                ]
            }
        )

    # TC01: JWT hợp lệ
    def test_valid_token(self):

        token = jwt.encode(
            self.payload,
            self.secret,
            algorithm=self.algorithm
        )

        decoded = self.decode_token(token)

        self.assertEqual(decoded["sub"], "1")
        self.assertEqual(decoded["type"], "access")
        self.assertEqual(decoded["ver"], 1)

    # TC02: JWT hết hạn
    def test_expired_token(self):

        now = datetime.now(timezone.utc)

        self.payload["iat"] = now - timedelta(hours=1)
        self.payload["exp"] = now - timedelta(minutes=1)

        token = jwt.encode(
            self.payload,
            self.secret,
            algorithm=self.algorithm
        )

        with self.assertRaises(jwt.ExpiredSignatureError):
            self.decode_token(token)

    # TC03 - TC07: Thiếu trường bắt buộc
    def test_missing_required_claims(self):

        required_claims = [
            "sub",
            "exp",
            "iat",
            "type",
            "ver"
        ]

        for claim in required_claims:

            with self.subTest(claim=claim):

                payload = self.payload.copy()

                payload.pop(claim)

                token = jwt.encode(
                    payload,
                    self.secret,
                    algorithm=self.algorithm
                )

                with self.assertRaises(
                    jwt.MissingRequiredClaimError
                ):
                    self.decode_token(token)

    # TC08: Thời điểm phát hành trong tương lai
    def test_future_issued_at(self):

        now = datetime.now(timezone.utc)

        self.payload["iat"] = now + timedelta(minutes=5)

        token = jwt.encode(
            self.payload,
            self.secret,
            algorithm=self.algorithm
        )

        with self.assertRaises(jwt.ImmatureSignatureError):
            self.decode_token(token)


if __name__ == "__main__":
    unittest.main(verbosity=2)
