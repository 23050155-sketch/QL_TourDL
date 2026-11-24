
import json
from getpass import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:8001"

results = []

ACCOUNT_FORBIDDEN = {
    "password",
    "password_hash",
    "token_version",
    "secret_key",
    "jwt_secret_key",
    "access_token",
}

GUIDE_PUBLIC_FIELDS = {
    "id",
    "full_name",
    "experience_years",
}

GUIDE_CONTACT_FIELDS = {
    "id",
    "full_name",
    "experience_years",
    "phone",
    "email",
}

REVIEW_PUBLIC_FIELDS = {
    "id",
    "tour_id",
    "rating",
    "comment",
    "created_at",
}

BOOKING_LIST_FIELDS = {
    "id",
    "user_id",
    "schedule_id",
    "number_of_people",
    "unit_price",
    "total_amount",
    "status",
    "created_at",
}

PAYMENT_FIELDS = {
    "id",
    "booking_id",
    "amount",
    "payment_method",
    "status",
    "transaction_code",
    "paid_at",
    "created_at",
}


# Gửi HTTP Request
def api_request(
    path,
    method="GET",
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
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=15) as response:
            return (
                response.status,
                json.loads(response.read()),
            )

    except HTTPError as error:
        return error.code, None

    except URLError:
        raise RuntimeError(
            "Không thể kết nối Backend"
        ) from None


# Ghi nhận kết quả
def record(name, passed=None):
    if passed is None:
        result = "SKIP"
    elif passed:
        result = "PASS"
    else:
        result = "FAIL"

    results.append(result)
    print(f"[{result}] {name}")


# Kiểm tra trường dữ liệu bị cấm
def contains_forbidden(data, forbidden):
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in forbidden:
                return True

            if contains_forbidden(value, forbidden):
                return True

    elif isinstance(data, list):
        for item in data:
            if contains_forbidden(item, forbidden):
                return True

    return False


# Kiểm tra danh sách JSON
def check_list_fields(name, data, allowed):
    if not isinstance(data, list):
        record(name, False)
        return

    if not data:
        record(name)
        return

    passed = all(
        isinstance(item, dict)
        and set(item.keys()) == allowed
        for item in data
    )

    record(name, passed)


# Đăng nhập và kiểm tra vai trò
def login(role):
    print(f"\nĐăng nhập {role.upper()}")

    email = input("Email: ").strip()
    password = getpass("Password: ")

    status, data = api_request(
        "/api/auth/login",
        method="POST",
        data={
            "email": email,
            "password": password,
        },
    )

    if status != 200:
        raise RuntimeError(
            f"Đăng nhập thất bại: HTTP {status}"
        )

    token = data["access_token"]

    status, profile = api_request(
        "/api/auth/me",
        token=token,
    )

    if status != 200 or profile["role"] != role:
        raise RuntimeError(
            f"Tài khoản không đúng vai trò {role}"
        )

    return token, profile


# 1. Kiểm tra thông tin tài khoản
def test_accounts(
    customer_profile,
    admin_profile,
    admin_token,
):
    print("\n=== ACCOUNT PRIVACY ===")

    record(
        "CUSTOMER profile không chứa dữ liệu bí mật",
        not contains_forbidden(
            customer_profile,
            ACCOUNT_FORBIDDEN,
        ),
    )

    record(
        "ADMIN profile không chứa dữ liệu bí mật",
        not contains_forbidden(
            admin_profile,
            ACCOUNT_FORBIDDEN,
        ),
    )

    status, data = api_request(
        "/api/users/",
        token=admin_token,
    )

    record("ADMIN xem danh sách tài khoản", status == 200)

    if status == 200:
        items = data.get("items", [])

        record(
            "Danh sách tài khoản không chứa dữ liệu bí mật",
            not contains_forbidden(
                items,
                ACCOUNT_FORBIDDEN,
            ) if items else None,
        )


# 2. Kiểm tra thông tin hướng dẫn viên
def test_guides(customer_token, admin_token):
    print("\n=== GUIDE PRIVACY ===")

    status, guides = api_request("/api/guides/")

    record("GUEST xem HDV công khai", status == 200)

    if status == 200:
        check_list_fields(
            "HDV công khai chỉ chứa trường được phép",
            guides,
            GUIDE_PUBLIC_FIELDS,
        )

        if guides:
            guide_id = guides[0]["id"]

            status, detail = api_request(
                f"/api/guides/{guide_id}"
            )

            record(
                "Chi tiết HDV công khai an toàn",
                status == 200
                and set(detail.keys()) == GUIDE_PUBLIC_FIELDS,
            )

    status, _ = api_request("/api/guides/admin/all")

    record(
        "GUEST không được xem HDV quản trị",
        status in (401, 403),
    )

    status, _ = api_request(
        "/api/guides/admin/all",
        token=customer_token,
    )

    record(
        "CUSTOMER không được xem HDV quản trị",
        status == 403,
    )

    status, guides = api_request(
        "/api/guides/admin/all",
        token=admin_token,
    )

    record("ADMIN xem danh sách HDV", status == 200)

    if status == 200:
        record(
            "ADMIN được xem thông tin liên hệ",
            all(
                GUIDE_CONTACT_FIELDS.issubset(guide.keys())
                for guide in guides
            ) if guides else None,
        )

        inactive = next(
            (
                guide for guide in guides
                if guide["status"] == "inactive"
            ),
            None,
        )

        if inactive:
            status, _ = api_request(
                f"/api/guides/{inactive['id']}"
            )

            record(
                "HDV inactive không hiển thị công khai",
                status == 404,
            )
        else:
            record("HDV inactive không hiển thị công khai")


# 3. Kiểm tra thông tin đánh giá
def test_reviews(customer_token, admin_token):
    print("\n=== REVIEW PRIVACY ===")

    status, tours = api_request("/api/tours/")

    record("Lấy danh sách Tour công khai", status == 200)

    if status == 200:
        found_review = False

        for tour in tours:
            status, reviews = api_request(
                f"/api/reviews/tour/{tour['id']}"
            )

            if status != 200:
                record("API đánh giá công khai", False)
                continue

            if reviews:
                found_review = True

                check_list_fields(
                    f"Review công khai Tour {tour['id']}",
                    reviews,
                    REVIEW_PUBLIC_FIELDS,
                )

        if not found_review:
            record("Kiểm tra Review công khai có dữ liệu")

    status, reviews = api_request(
        "/api/reviews/my",
        token=customer_token,
    )

    record("CUSTOMER xem Review của mình", status == 200)

    if status == 200:
        record(
            "Review cá nhân vẫn chứa user_id",
            all("user_id" in item for item in reviews)
            if reviews else None,
        )

    status, reviews = api_request(
        "/api/reviews/admin",
        token=admin_token,
    )

    record("ADMIN xem Review quản trị", status == 200)

    if status == 200:
        record(
            "Review quản trị vẫn chứa user_id",
            all("user_id" in item for item in reviews)
            if reviews else None,
        )


# 4. Kiểm tra thông tin Booking
def test_bookings(
    customer_token,
    admin_token,
    customer_id,
):
    print("\n=== BOOKING PRIVACY ===")

    status, my_bookings = api_request(
        "/api/bookings/my",
        token=customer_token,
    )

    record("CUSTOMER xem danh sách Booking", status == 200)

    if status != 200:
        my_bookings = []
    else:
        check_list_fields(
            "Danh sách CUSTOMER không chứa passengers",
            my_bookings,
            BOOKING_LIST_FIELDS,
        )

        record(
            "CUSTOMER chỉ nhận Booking của mình",
            all(
                item["user_id"] == customer_id
                for item in my_bookings
            ) if my_bookings else None,
        )

    status, all_bookings = api_request(
        "/api/bookings/admin/all",
        token=admin_token,
    )

    record("ADMIN xem danh sách Booking", status == 200)

    if status != 200:
        all_bookings = []
    else:
        check_list_fields(
            "Danh sách ADMIN không chứa passengers",
            all_bookings,
            BOOKING_LIST_FIELDS,
        )

    if my_bookings:
        booking_id = my_bookings[0]["id"]

        status, detail = api_request(
            f"/api/bookings/{booking_id}",
            token=customer_token,
        )

        record(
            "Chi tiết Booking chứa passengers",
            status == 200
            and isinstance(detail.get("passengers"), list),
        )
    else:
        record("Chi tiết Booking chứa passengers")

    if all_bookings:
        booking_id = all_bookings[0]["id"]

        status, detail = api_request(
            f"/api/bookings/admin/{booking_id}",
            token=admin_token,
        )

        record(
            "ADMIN xem chi tiết hành khách",
            status == 200
            and isinstance(detail.get("passengers"), list),
        )
    else:
        record("ADMIN xem chi tiết hành khách")

    other_booking = next(
        (
            item for item in all_bookings
            if item["user_id"] != customer_id
        ),
        None,
    )

    if other_booking:
        booking_id = other_booking["id"]

        status, _ = api_request(
            f"/api/bookings/{booking_id}",
            token=customer_token,
        )

        record(
            "Không xem Booking của người khác",
            status == 404,
        )

        status, _ = api_request(
            f"/api/bookings/{booking_id}/guides",
            token=customer_token,
        )

        record(
            "Không xem HDV của Booking người khác",
            status == 404,
        )
    else:
        record("Không xem Booking của người khác")
        record("Không xem HDV của Booking người khác")

    return my_bookings


# 5. Kiểm tra quyền xem liên hệ HDV
def test_guide_contacts(my_bookings, customer_token):
    print("\n=== GUIDE CONTACT PRIVACY ===")

    if not my_bookings:
        record("Kiểm tra liên hệ HDV theo Booking")
        return

    for booking in my_bookings:
        booking_id = booking["id"]
        booking_status = booking["status"]

        status, guides = api_request(
            f"/api/bookings/{booking_id}/guides",
            token=customer_token,
        )

        expected = 200 if booking_status == "paid" else 403

        record(
            f"Booking {booking_id} ({booking_status})",
            status == expected,
        )

        if booking_status == "paid" and status == 200:
            check_list_fields(
                f"Thông tin liên hệ Booking {booking_id}",
                guides,
                GUIDE_CONTACT_FIELDS,
            )


# 6. Kiểm tra thông tin thanh toán
def test_payments(
    customer_token,
    admin_token,
    my_bookings,
):
    print("\n=== PAYMENT PRIVACY ===")

    status, payments = api_request(
        "/api/payments/my",
        token=customer_token,
    )

    record("CUSTOMER xem thanh toán", status == 200)

    if status == 200:
        check_list_fields(
            "Response thanh toán CUSTOMER an toàn",
            payments,
            PAYMENT_FIELDS,
        )

        booking_ids = {
            item["id"] for item in my_bookings
        }

        record(
            "Thanh toán chỉ thuộc Booking của mình",
            all(
                item["booking_id"] in booking_ids
                for item in payments
            ) if payments else None,
        )

    status, payments = api_request(
        "/api/payments/admin/all",
        token=admin_token,
    )

    record("ADMIN xem thanh toán", status == 200)

    if status == 200:
        check_list_fields(
            "Response thanh toán ADMIN an toàn",
            payments,
            PAYMENT_FIELDS,
        )

    status, _ = api_request("/api/payments/my")

    record(
        "GUEST không được xem thanh toán",
        status in (401, 403),
    )

    status, _ = api_request(
        "/api/payments/admin/all",
        token=customer_token,
    )

    record(
        "CUSTOMER không xem thanh toán quản trị",
        status == 403,
    )


# 7. Kiểm tra dữ liệu thanh toán không hợp lệ
def test_payment_input(customer_token):
    print("\n=== PAYMENT INPUT VALIDATION ===")

    invalid_fields = {
        "amount": 1000,
        "status": "success",
        "user_id": 1,
        "transaction_code": "TEST-PRIVACY",
    }

    for field, value in invalid_fields.items():
        # Booking ID bằng 0 để tránh tạo giao dịch
        # nếu cấu hình extra="forbid" chưa hoạt động.
        payload = {
            "booking_id": 0,
            "payment_method": "cash",
            field: value,
        }

        request = Request(
            BASE_URL + "/api/payments/",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {customer_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=15):
                record(f"Từ chối trường {field}", False)

        except HTTPError as error:
            if error.code != 422:
                record(f"Từ chối trường {field}", False)
                continue

            data = json.loads(error.read())

            extra_error = any(
                item.get("type") == "extra_forbidden"
                and item.get("loc", [])[-1:] == [field]
                for item in data.get("detail", [])
            )

            record(f"Từ chối trường {field}", extra_error)


# Tổng hợp kết quả
def print_summary():
    total = len(results)
    passed = results.count("PASS")
    failed = results.count("FAIL")
    skipped = results.count("SKIP")

    executed = passed + failed

    success_rate = (
        passed / executed * 100
        if executed else 0
    )

    print("\n" + "=" * 45)
    print("DATA PRIVACY TEST SUMMARY")
    print("=" * 45)
    print(f"Total        : {total}")
    print(f"Passed       : {passed}")
    print(f"Failed       : {failed}")
    print(f"Skipped      : {skipped}")
    print(f"Success rate : {success_rate:.2f}%")

    if failed:
        print("SOME TESTS FAILED")
    elif skipped:
        print("EXECUTED TESTS PASSED - SOME SKIPPED")
    elif executed:
        print("ALL TESTS PASSED")
    else:
        print("NO TESTS EXECUTED")

    return 1 if failed or not executed else 0


def main():
    print("=" * 45)
    print("HTTT16 - DATA PRIVACY SECURITY TEST")
    print("=" * 45)

    customer_token, customer_profile = login("customer")
    admin_token, admin_profile = login("admin")

    test_accounts(
        customer_profile,
        admin_profile,
        admin_token,
    )

    test_guides(customer_token, admin_token)

    test_reviews(customer_token, admin_token)

    my_bookings = test_bookings(
        customer_token,
        admin_token,
        customer_profile["id"],
    )

    test_guide_contacts(
        my_bookings,
        customer_token,
    )

    test_payments(
        customer_token,
        admin_token,
        my_bookings,
    )

    test_payment_input(customer_token)

    return print_summary()


if __name__ == "__main__":
    try:
        raise SystemExit(main())

    except (RuntimeError, URLError, ValueError) as error:
        print(f"\nLỗi kiểm thử: {error}")
        raise SystemExit(1)

    except KeyboardInterrupt:
        print("\nĐã dừng kiểm thử")
        raise SystemExit(1)
