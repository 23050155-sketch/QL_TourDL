
import json
from getpass import getpass
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE_URL = "http://127.0.0.1:8001"
TIMEOUT = 15


# ==================================================
# 1. HTTP REQUEST
# ==================================================

def request_api(
    path,
    params=None,
    token=None,
    method="GET",
    data=None
):
    url = BASE_URL + path

    if params:
        url += "?" + urlencode(params)

    headers = {
        "Accept": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            status = response.status
            raw = response.read()

    except HTTPError as exc:
        status = exc.code
        raw = exc.read()

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        payload = None

    return status, payload


# ==================================================
# 2. LOGIN
# ==================================================

def login(role):
    print(f"\nLogin as {role.upper()}")

    email = input("Email: ").strip()
    password = getpass("Password: ")

    status, payload = request_api(
        "/api/auth/login",
        method="POST",
        data={
            "email": email,
            "password": password
        }
    )

    if status != 200 or not isinstance(payload, dict):
        raise RuntimeError(
            f"Login failed: HTTP {status}"
        )

    token = payload.get("access_token")

    if not token:
        raise RuntimeError("Missing access token")

    status, profile = request_api(
        "/api/auth/me",
        token=token
    )

    if (
        status != 200
        or not isinstance(profile, dict)
        or profile.get("role") != role
    ):
        raise RuntimeError(
            f"Account must have role: {role}"
        )

    print("Login successful")

    return token


# ==================================================
# 3. TEST RUNNER
# ==================================================

class TestRunner:

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def check(self, name, condition):
        if condition:
            self.passed += 1
            print(f"[PASS] {name}")
        else:
            self.failed += 1
            print(f"[FAIL] {name}")

    def skip(self, name, reason):
        self.skipped += 1
        print(f"[SKIP] {name}: {reason}")

    def status(
        self,
        name,
        path,
        expected,
        params=None,
        token=None
    ):
        try:
            actual, payload = request_api(
                path,
                params=params,
                token=token
            )

            self.check(
                f"{name} | expected={expected}, actual={actual}",
                actual == expected
            )

            return actual, payload

        except Exception as exc:
            self.check(
                f"{name} | {type(exc).__name__}",
                False
            )

            return None, None

    def summary(self):
        total = (
            self.passed
            + self.failed
            + self.skipped
        )

        executed = self.passed + self.failed

        rate = (
            self.passed / executed * 100
            if executed
            else 0
        )

        print("\n" + "=" * 60)
        print("SEARCH SECURITY TEST SUMMARY")
        print("=" * 60)
        print(f"Total: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Skipped: {self.skipped}")
        print(f"Success rate: {rate:.2f}%")

        if self.failed:
            print("SOME TESTS FAILED")
        elif self.skipped:
            print("EXECUTED TESTS PASSED - SOME SKIPPED")
        else:
            print("ALL TESTS PASSED")


# ==================================================
# 4. PAGINATION RESPONSE VALIDATION
# ==================================================

def valid_pagination_response(payload, page, page_size):
    if not isinstance(payload, dict):
        return False

    required_fields = {
        "total",
        "page",
        "page_size",
        "total_pages",
        "items"
    }

    if not required_fields.issubset(payload):
        return False

    total = payload["total"]
    total_pages = payload["total_pages"]
    items = payload["items"]

    if type(total) is not int or total < 0:
        return False

    if type(total_pages) is not int:
        return False

    if not isinstance(items, list):
        return False

    if not all(isinstance(item, dict) for item in items):
        return False

    if payload["page"] != page:
        return False

    if payload["page_size"] != page_size:
        return False

    expected_pages = (
        total + page_size - 1
    ) // page_size

    if total_pages != expected_pages:
        return False

    expected_count = min(
        page_size,
        max(0, total - (page - 1) * page_size)
    )

    return len(items) == expected_count


# ==================================================
# 5. PAGINATION TESTS
# ==================================================

def test_pagination(runner, path, label, token=None):
    cases = [
        (1, 10, 200),
        (2, 10, 200),
        (1, 100, 200),
        (101, 100, 200),
        (501, 20, 200),
        (10001, 1, 200),
        (1, 1, 200),

        (0, 10, 422),
        (-1, 10, 422),
        (1, 0, 422),
        (1, 101, 422),
        (102, 100, 422),
        (502, 20, 422),
        (10002, 1, 422),
        (999999999, 100, 422),
        (1.5, 10, 422),
        (1, 2.5, 422),
    ]

    for page, page_size, expected in cases:

        name = (
            f"{label}: page={page}, "
            f"page_size={page_size}"
        )

        actual, payload = runner.status(
            name,
            path,
            expected,
            params={
                "page": page,
                "page_size": page_size
            },
            token=token
        )

        if expected == 200:
            runner.check(
                name + " response structure",
                actual == 200
                and valid_pagination_response(
                    payload,
                    page,
                    page_size
                )
            )


# ==================================================
# 6. TOUR SEARCH TESTS
# ==================================================

def test_tour_search(runner):
    path = "/api/tours/search"

    cases = [
        ("Default search", {}, 200),

        ("Vietnamese keyword",
         {"search": "Đà Lạt"}, 200),

        ("Whitespace keyword",
         {"search": "  Đà   Lạt  "}, 200),

        ("Blank keyword",
         {"search": "   "}, 200),

        ("Percent keyword",
         {"search": "%"}, 200),

        ("Underscore keyword",
         {"search": "_"}, 200),

        ("Apostrophe keyword",
         {"search": "O'Brien"}, 200),

        ("Maximum search length",
         {"search": "A" * 255}, 200),

        ("Search too long",
         {"search": "A" * 256}, 422),

        ("Invalid control character",
         {"search": "Tour\x00"}, 422),

        ("Province search",
         {"province": "  Lâm   Đồng  "}, 200),

        ("Province too long",
         {"province": "A" * 151}, 422),

        ("Valid price range",
         {"min_price": "1000000",
          "max_price": "5000000"}, 200),

        ("Reversed price range",
         {"min_price": "5000000",
          "max_price": "1000000"}, 400),

        ("Negative price",
         {"min_price": "-1"}, 422),

        ("Maximum allowed price",
         {"max_price": "9999999999.99"}, 200),

        ("Price overflow",
         {"max_price": "10000000000"}, 422),

        ("Invalid decimal places",
         {"min_price": "100.123"}, 422),

        ("Trailing decimal zeros",
         {"min_price": "100.1200"}, 200),

        ("NaN price",
         {"min_price": "NaN"}, 422),

        ("Infinite price",
         {"max_price": "Infinity"}, 422),

        ("Valid duration",
         {"duration_days": 3}, 200),

        ("Zero duration",
         {"duration_days": 0}, 422),

        ("Duration overflow",
         {"duration_days": 366}, 422),

        ("Invalid sort option",
         {"sort_by": "unknown"}, 422),
    ]

    for name, params, expected in cases:
        runner.status(
            "Tour: " + name,
            path,
            expected,
            params=params
        )

    sort_options = [
        "newest",
        "oldest",
        "price_asc",
        "price_desc",
        "duration_asc",
        "duration_desc",
    ]

    for option in sort_options:
        runner.status(
            f"Tour: sort_by={option}",
            path,
            200,
            params={"sort_by": option}
        )


# ==================================================
# 7. USER SEARCH TESTS
# ==================================================

def test_user_search(runner, admin_token):
    path = "/api/users/"

    cases = [
        ("Default search", {}, 200),

        ("Vietnamese keyword",
         {"search": "Nguyễn"}, 200),

        ("Whitespace keyword",
         {"search": "  Nguyễn   Văn  "}, 200),

        ("Blank keyword",
         {"search": "   "}, 200),

        ("Email search",
         {"search": "@example.com"}, 200),

        ("Phone search",
         {"search": "090"}, 200),

        ("Percent keyword",
         {"search": "%"}, 200),

        ("Underscore keyword",
         {"search": "_"}, 200),

        ("Apostrophe keyword",
         {"search": "O'Brien"}, 200),

        ("Maximum search length",
         {"search": "A" * 150}, 200),

        ("Search too long",
         {"search": "A" * 151}, 422),

        ("Invalid control character",
         {"search": "User\x00"}, 422),

        ("Active customers",
         {"status": "active"}, 200),

        ("Inactive customers",
         {"status": "inactive"}, 200),

        ("Invalid status",
         {"status": "unknown"}, 422),
    ]

    for name, params, expected in cases:
        runner.status(
            "User: " + name,
            path,
            expected,
            params=params,
            token=admin_token
        )


# ==================================================
# 8. DATA CONSISTENCY
# ==================================================

def get_items(payload):
    if not isinstance(payload, dict):
        return None

    items = payload.get("items")

    if not isinstance(items, list):
        return None

    if not all(
        isinstance(item, dict)
        and type(item.get("id")) is int
        for item in items
    ):
        return None

    return items


def test_consistency(
    runner,
    path,
    label,
    keyword,
    token=None
):
    status1, data1 = request_api(
        path,
        params={"search": keyword},
        token=token
    )

    status2, data2 = request_api(
        path,
        params={
            "search": "  " + keyword.replace(" ", "   ") + "  "
        },
        token=token
    )

    items1 = get_items(data1)
    items2 = get_items(data2)

    runner.check(
        f"{label}: normalized search consistency",
        status1 == 200
        and status2 == 200
        and items1 is not None
        and items2 is not None
        and data1.get("total") == data2.get("total")
        and [item["id"] for item in items1]
        == [item["id"] for item in items2]
    )

    if items1 is not None and not items1:
        runner.skip(
            f"{label}: non-empty normalization fixture",
            "No matching records"
        )
    else:
        runner.check(
            f"{label}: non-empty normalization fixture",
            status1 == 200 and bool(items1)
        )

    status1, data1 = request_api(
        path,
        params={"page": 1, "page_size": 2},
        token=token
    )

    status2, data2 = request_api(
        path,
        params={"page": 2, "page_size": 2},
        token=token
    )

    items1 = get_items(data1)
    items2 = get_items(data2)

    if (
        status1 != 200
        or status2 != 200
        or items1 is None
        or items2 is None
    ):
        runner.check(
            f"{label}: pagination consistency",
            False
        )

    elif not items2:
        runner.skip(
            f"{label}: pagination consistency",
            "Not enough records for second page"
        )

    else:
        ids1 = {item["id"] for item in items1}
        ids2 = {item["id"] for item in items2}

        runner.check(
            f"{label}: no duplicate IDs between pages",
            ids1.isdisjoint(ids2)
        )


# ==================================================
# 9. PRIVACY AND ROLE CHECKS
# ==================================================

def test_access_and_privacy(
    runner,
    admin_token,
    customer_token
):
    status, _ = request_api("/api/users/")

    runner.check(
        "Guest cannot access customer list",
        status in (401, 403)
    )

    runner.status(
        "Customer cannot access customer list",
        "/api/users/",
        403,
        token=customer_token
    )

    status, payload = runner.status(
        "Admin can access customer list",
        "/api/users/",
        200,
        token=admin_token
    )

    items = get_items(payload)

    if status != 200 or items is None:
        runner.check("Customer privacy response", False)

    elif not items:
        runner.skip(
            "Customer privacy response",
            "No customer records"
        )

    else:
        runner.check(
            "Only customer accounts returned",
            all(
                item.get("role") == "customer"
                for item in items
            )
        )

        runner.check(
            "Sensitive fields are not exposed",
            all(
                "password_hash" not in item
                and "password" not in item
                and "token_version" not in item
                for item in items
            )
        )

    status, payload = request_api("/api/tours/search")
    items = get_items(payload)

    if status != 200 or items is None:
        runner.check("Only active tours returned", False)

    elif not items:
        runner.skip(
            "Only active tours returned",
            "No active tours"
        )

    else:
        runner.check(
            "Only active tours returned",
            all(
                item.get("status") == "active"
                for item in items
            )
        )


# ==================================================
# 10. MAIN
# ==================================================

def main():
    print("=" * 60)
    print("HTTT16 - SEARCH & PAGINATION SECURITY TEST")
    print("=" * 60)

    runner = TestRunner()

    try:
        admin_token = login("admin")
        customer_token = login("customer")

        print("\n--- TOUR SEARCH ---")
        test_tour_search(runner)

        print("\n--- USER SEARCH ---")
        test_user_search(runner, admin_token)

        print("\n--- TOUR PAGINATION ---")
        test_pagination(
            runner,
            "/api/tours/search",
            "Tour"
        )

        print("\n--- USER PAGINATION ---")
        test_pagination(
            runner,
            "/api/users/",
            "User",
            admin_token
        )

        print("\n--- DATA CONSISTENCY ---")

        test_consistency(
            runner,
            "/api/tours/search",
            "Tour",
            "Đà Lạt"
        )

        test_consistency(
            runner,
            "/api/users/",
            "User",
            "Nguyễn Văn",
            admin_token
        )

        print("\n--- ACCESS AND PRIVACY ---")

        test_access_and_privacy(
            runner,
            admin_token,
            customer_token
        )

    except Exception as exc:
        runner.check(
            f"Test execution error: {type(exc).__name__}",
            False
        )

    runner.summary()

    return 1 if runner.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
