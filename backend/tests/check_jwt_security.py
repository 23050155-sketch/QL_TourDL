
import json
from getpass import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:8001"

results = []


# Gửi yêu cầu HTTP đến Backend
def call_api(method, path, token=None, data=None):

    headers = {
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url=BASE_URL + path,
        data=body,
        headers=headers,
        method=method
    )

    try:

        with urlopen(request, timeout=15) as response:

            content = response.read().decode("utf-8")

            return response.status, json.loads(content)

    except HTTPError as error:

        content = error.read().decode("utf-8")

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = {}

        return error.code, data


# Kiểm tra kết quả của từng Test Case
def check(name, actual, expected):

    passed = actual == expected

    results.append(passed)

    status = "PASS" if passed else "FAIL"

    print(
        f"[{status}] {name} | "
        f"Expected: {expected} | "
        f"Actual: {actual}"
    )


# Chương trình kiểm thử chính
def main():

    results.clear()

    print("=" * 65)
    print("HTTT16 - JWT SECURITY TEST")
    print("=" * 65)

    email = input("Email CUSTOMER test: ").strip()
    password = getpass("Password: ")

    # Đăng nhập tài khoản thử nghiệm
    status, data = call_api(
        "POST",
        "/api/auth/login",
        data={
            "email": email,
            "password": password
        }
    )

    check("TC01 - Login", status, 200)

    if status != 200:
        print("Login failed. Stop testing.")
        return

    token = data["access_token"]

    # Kiểm tra JWT hợp lệ
    status, profile = call_api(
        "GET",
        "/api/auth/me",
        token
    )

    check("TC02 - Valid JWT", status, 200)

    if status != 200 or profile.get("role") != "customer":
        print("Please use a CUSTOMER test account.")
        return

    # Kiểm tra JWT sai định dạng
    status, _ = call_api(
        "GET",
        "/api/auth/me",
        "invalid-token"
    )

    check("TC03 - Invalid JWT", status, 401)

    # Kiểm tra JWT có chữ ký bị thay đổi
    parts = token.split(".")

    signature = parts[2]

    replacement = "A" if signature[0] != "A" else "B"

    parts[2] = replacement + signature[1:]

    invalid_token = ".".join(parts)

    status, _ = call_api(
        "GET",
        "/api/auth/me",
        invalid_token
    )

    check("TC04 - Invalid signature", status, 401)

    # Kiểm tra phân quyền CUSTOMER
    status, _ = call_api(
        "GET",
        "/api/auth/admin-test",
        token
    )

    check("TC05 - Customer access admin", status, 403)

    # Đăng xuất
    status, _ = call_api(
        "POST",
        "/api/auth/logout",
        token
    )

    check("TC06 - Logout", status, 200)

    # Kiểm tra JWT sau khi đăng xuất
    status, _ = call_api(
        "GET",
        "/api/auth/me",
        token
    )

    check("TC07 - Revoked JWT", status, 401)

    # Đăng xuất lại bằng JWT cũ
    status, _ = call_api(
        "POST",
        "/api/auth/logout",
        token
    )

    check("TC08 - Repeated logout", status, 401)

    # Đăng nhập lại
    status, data = call_api(
        "POST",
        "/api/auth/login",
        data={
            "email": email,
            "password": password
        }
    )

    check("TC09 - Login again", status, 200)

    if status == 200:

        new_token = data["access_token"]

        status, _ = call_api(
            "GET",
            "/api/auth/me",
            new_token
        )

        check("TC10 - New JWT", status, 200)

    else:
        print("[SKIP] TC10 - Login failed")

    # Tổng hợp kết quả
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print("=" * 65)
    print(f"Executed: {total}/10")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {10 - total}")

    if passed == 10:
        print("RESULT: ALL TESTS PASSED")
    else:
        print("RESULT: TESTS FAILED OR INCOMPLETE")

    print("=" * 65)


if __name__ == "__main__":

    try:
        main()

    except URLError:
        print("Cannot connect to Backend.")

    except KeyboardInterrupt:
        print("\nTesting cancelled.")
