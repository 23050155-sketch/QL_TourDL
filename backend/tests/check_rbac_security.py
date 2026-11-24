
import json
import sys
from getpass import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:8001"


# 1. Hàm gửi HTTP Request
def send_request(
    method,
    path,
    token=None,
    data=None,
):
    headers = {
        "Accept": "application/json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url=BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=15) as response:
            content = response.read().decode("utf-8")

            return (
                response.status,
                json.loads(content) if content else None,
            )

    except HTTPError as error:
        return error.code, None

    except URLError:
        raise RuntimeError(
            "Không thể kết nối Backend"
        )


# 2. Đăng nhập tài khoản kiểm thử
def login(role):
    print(f"\nĐăng nhập tài khoản {role.upper()}")

    email = input("Email: ").strip()
    password = getpass("Password: ")

    status, result = send_request(
        method="POST",
        path="/api/auth/login",
        data={
            "email": email,
            "password": password,
        },
    )

    if status != 200 or not result:
        raise RuntimeError(
            f"Đăng nhập thất bại: HTTP {status}"
        )

    token = result["access_token"]

    # Xác nhận vai trò thực tế của tài khoản
    status, profile = send_request(
        method="GET",
        path="/api/auth/me",
        token=token,
    )

    if (
        status != 200
        or not profile
        or profile.get("role") != role
    ):
        raise RuntimeError(
            f"Tài khoản không có vai trò {role}"
        )

    print(f"Đăng nhập {role.upper()} thành công")

    return token


# 3. Danh sách API công khai
PUBLIC_ENDPOINTS = [
    "/api/tours/",
    "/api/tours/search",
    "/api/departures/",
    "/api/destinations/",
    "/api/guides/",
]


# 4. Danh sách API dành cho CUSTOMER
CUSTOMER_ENDPOINTS = [
    "/api/bookings/my",
    "/api/payments/my",
    "/api/reviews/my",
]


# 5. Danh sách API dành cho ADMIN
ADMIN_ENDPOINTS = [
    "/api/auth/admin-test",
    "/api/users/",
    "/api/tours/admin/all",
    "/api/departures/admin/all",
    "/api/bookings/admin/all",
    "/api/payments/admin/all",
    "/api/reviews/admin",
    "/api/guide-assignments/",
    "/api/dashboard/overview",
    "/api/dashboard/booking-status",
    "/api/dashboard/monthly-revenue",
    "/api/dashboard/top-tours",
    "/api/dashboard/recent-bookings",
    "/api/guides/admin/all",
]


# 6. Chạy một Test Case
def run_test(role, token, path, expected):
    actual, _ = send_request(
        method="GET",
        path=path,
        token=token,
    )

    passed = actual in expected

    result = "PASS" if passed else "FAIL"

    expected_text = "/".join(
        str(code) for code in expected
    )

    print(
        f"[{result}] "
        f"{role:<10} "
        f"GET {path:<40} "
        f"Expected: {expected_text:<7} "
        f"Actual: {actual}"
    )

    return passed


# 7. Chương trình chính
def main():
    print("=" * 75)
    print("HTTT16 - KIEM THU BAO MAT RBAC")
    print("=" * 75)

    customer_token = login("customer")
    admin_token = login("admin")

    roles = {
        "GUEST": None,
        "CUSTOMER": customer_token,
        "ADMIN": admin_token,
    }

    total = 0
    passed = 0

    for role, token in roles.items():

        print(f"\n{'=' * 75}")
        print(f"KIEM THU VAI TRO: {role}")
        print("=" * 75)

        # API công khai
        for path in PUBLIC_ENDPOINTS:
            total += 1

            if run_test(
                role, token, path, (200,)
            ):
                passed += 1

        # API CUSTOMER
        for path in CUSTOMER_ENDPOINTS:

            if role == "CUSTOMER":
                expected = (200,)

            elif role == "GUEST":
                expected = (401, 403)

            else:
                expected = (403,)

            total += 1

            if run_test(
                role, token, path, expected
            ):
                passed += 1

        # API ADMIN
        for path in ADMIN_ENDPOINTS:

            if role == "ADMIN":
                expected = (200,)

            elif role == "GUEST":
                expected = (401, 403)

            else:
                expected = (403,)

            total += 1

            if run_test(
                role, token, path, expected
            ):
                passed += 1

    failed = total - passed

    print("\n" + "=" * 75)
    print("KET QUA KIEM THU RBAC")
    print("=" * 75)

    print(f"Total : {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    print(
        f"Success rate: "
        f"{passed / total * 100:.2f}%"
    )

    if failed == 0:
        print("\nALL TESTS PASSED")
        return 0

    print("\nSOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())

    except (RuntimeError, TimeoutError) as error:
        print(f"\nERROR: {error}")
        sys.exit(1)
