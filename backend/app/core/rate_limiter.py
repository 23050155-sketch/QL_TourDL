
from collections import deque
from threading import Lock
from time import monotonic
from math import ceil

from fastapi import HTTPException


class RateLimiter:

    def __init__(
        self,
        max_requests: int = 5,
        window_seconds: int = 60,
        max_keys: int = 10000
    ):

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_keys = max_keys

        # Lưu thời điểm gửi yêu cầu theo từng IP
        self.requests: dict[str, deque[float]] = {}

        # Bảo vệ dữ liệu khi nhiều request chạy đồng thời
        self.lock = Lock()

    def check(self, key: str) -> None:

        with self.lock:

            now = monotonic()
            cutoff = now - self.window_seconds

            # Dọn dữ liệu đã hết hạn
            expired_keys = []

            for saved_key, timestamps in self.requests.items():

                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()

                if not timestamps:
                    expired_keys.append(saved_key)

            for expired_key in expired_keys:
                del self.requests[expired_key]

            # Giới hạn số lượng IP lưu trong bộ nhớ
            if key not in self.requests:

                if len(self.requests) >= self.max_keys:

                    raise HTTPException(
                        status_code=429,
                        detail="Hệ thống đang giới hạn yêu cầu",
                        headers={
                            "Retry-After": str(self.window_seconds)
                        }
                    )

                self.requests[key] = deque()

            timestamps = self.requests[key]

            # Kiểm tra số lần gửi yêu cầu
            if len(timestamps) >= self.max_requests:

                retry_after = max(
                    1,
                    ceil(
                        timestamps[0]
                        + self.window_seconds
                        - now
                    )
                )

                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Bạn đã đăng nhập quá nhiều lần. "
                        "Vui lòng thử lại sau."
                    ),
                    headers={
                        "Retry-After": str(retry_after)
                    }
                )

            # Ghi nhận yêu cầu hiện tại
            timestamps.append(now)


# Rate Limiter dành riêng cho API đăng nhập
login_rate_limiter = RateLimiter(
    max_requests=5,
    window_seconds=60,
    max_keys=10000
)
