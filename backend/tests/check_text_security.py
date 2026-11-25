
import json

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


BASE_URL = "http://127.0.0.1:8001"
TIMEOUT = 15


# ==================================================
# 1. HTTP REQUEST HELPER
# ==================================================

def request_api(
    method,
    path,
    params=None,
    body=None,
):

    url = BASE_URL + path

    if params:
        url += "?" + urlencode(params)

    headers = {
        "Accept": "application/json",
    }

    data = None

    if body is not None:
        headers["Content-Type"] = "application/json"

        data = json.dumps(
            body,
            ensure_ascii=True,
        ).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(
            request,
            timeout=TIMEOUT,
        ) as response:

            status = response.status
            response_headers = response.headers
            raw_body = response.read()

    except HTTPError as exc:

        status = exc.code
        response_headers = exc.headers
        raw_body = exc.read()

    try:
        response_body = json.loads(
            raw_body.decode("utf-8")
        )

    except (ValueError, UnicodeError):
        response_body = None

    return (
        status,
        response_headers,
        response_body,
    )


# ==================================================
# 2. TEST RUNNER
# ==================================================

class TestRunner:

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def check(self, name, condition):

        if condition:
            self.passed += 1
            print(f"[PASS] {name}")

        else:
            self.failed += 1
            print(f"[FAIL] {name}")

    def api_check(
        self,
        name,
        method,
        path,
        expected_status,
        params=None,
        body=None,
        expected_type="application/json",
    ):

        try:
            status, headers, result = request_api(
                method,
                path,
                params=params,
                body=body,
            )

        except Exception as exc:

            self.check(
                f"{name}: request failed "
                f"({type(exc).__name__})",
                False,
            )

            return None

        # HTTP status
        self.check(
            f"{name}: HTTP status {status}",
            status == expected_status,
        )

        # Content-Type
        content_type = headers.get(
            "Content-Type",
            "",
        ).split(";", 1)[0].strip().lower()

        self.check(
            f"{name}: Content-Type",
            content_type == expected_type,
        )

        # Security header
        self.check(
            f"{name}: nosniff",
            headers.get(
                "X-Content-Type-Options",
                "",
            ).lower() == "nosniff",
        )

        # JSON response
        if expected_type == "application/json":

            self.check(
                f"{name}: valid JSON",
                isinstance(result, (dict, list)),
            )

        return result

    def summary(self):

        total = self.passed + self.failed

        rate = (
            self.passed / total * 100
            if total
            else 0
        )

        print("=" * 60)
        print("TEXT SECURITY API TEST SUMMARY")
        print("=" * 60)
        print(f"Total: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {rate:.2f}%")

        if self.failed:
            print("SOME TESTS FAILED")
            return False

        print("ALL TESTS PASSED")
        return True


# ==================================================
# 3. JSON RESPONSE AND SECURITY HEADERS
# ==================================================

def test_response_security(runner):

    runner.api_check(
        "Public tour list",
        "GET",
        "/api/tours/",
        200,
    )

    runner.api_check(
        "Tour search",
        "GET",
        "/api/tours/search",
        200,
    )

    runner.api_check(
        "Invalid pagination",
        "GET",
        "/api/tours/search",
        422,
        params={"page": 0},
    )

    runner.api_check(
        "Not found",
        "GET",
        "/api/not-found-test",
        404,
    )

    runner.api_check(
        "Swagger UI",
        "GET",
        "/docs",
        200,
        expected_type="text/html",
    )

    runner.api_check(
        "OpenAPI JSON",
        "GET",
        "/openapi.json",
        200,
    )


# ==================================================
# 4. SEARCH TEXT SECURITY
# ==================================================

def test_search_security(runner):

    valid_cases = [
        ("Vietnamese", "Đà Lạt"),
        ("Whitespace", "  Tour   Đà Lạt  "),
        ("Plain punctuation", "A & B < C > D"),
        ("Plain markup", "<b>Tour</b>"),
        ("Blank keyword", "   "),
    ]

    for name, keyword in valid_cases:

        runner.api_check(
            name,
            "GET",
            "/api/tours/search",
            200,
            params={"search": keyword},
        )

    invalid_cases = [
        ("NULL character", "Tour\x00"),
        ("Escape character", "Tour\x1b"),
        ("DEL character", "Tour\x7f"),
        ("C1 control", "Tour\x85"),
        ("Vertical tab", "Tour\x0b"),
    ]

    for name, keyword in invalid_cases:

        runner.api_check(
            name,
            "GET",
            "/api/tours/search",
            422,
            params={"search": keyword},
        )


# ==================================================
# 5. REQUEST VALIDATION AND ERROR PRIVACY
# ==================================================

def test_request_validation(runner):

    invalid_cases = [
        (
            "Register invalid name",
            "/api/auth/register",
            {
                "full_name": "Nguyễn\x00An",
                "email": "test@example.com",
                "password": "ExampleTest2026!",
            },
            "full_name",
        ),
        (
            "Register invalid email",
            "/api/auth/register",
            {
                "full_name": "Nguyễn Văn An",
                "email": "test@example.com\n",
                "password": "ExampleTest2026!",
            },
            "email",
        ),
        (
            "Register invalid phone",
            "/api/auth/register",
            {
                "full_name": "Nguyễn Văn An",
                "email": "test@example.com",
                "password": "ExampleTest2026!",
                "phone": "090\t1234567",
            },
            "phone",
        ),
        (
            "Login invalid email",
            "/api/auth/login",
            {
                "email": "test@example.com\n",
                "password": "ExampleTest2026!",
            },
            "email",
        ),
    ]

    for name, path, body, field in invalid_cases:

        result = runner.api_check(
            name,
            "POST",
            path,
            422,
            body=body,
        )

        errors = (
            result.get("detail", [])
            if isinstance(result, dict)
            else []
        )

        if not isinstance(errors, list):
            errors = []

        # Verify expected validation field
        runner.check(
            f"{name}: expected field",
            any(
                isinstance(error, dict)
                and error.get("loc") == [
                    "body",
                    field,
                ]
                for error in errors
            ),
        )

        # Verify validation error privacy
        runner.check(
            f"{name}: error privacy",
            bool(errors)
            and all(
                isinstance(error, dict)
                and "input" not in error
                and "ctx" not in error
                for error in errors
            )
            and isinstance(result, dict)
            and "body" not in result,
        )

        serialized = json.dumps(
            result,
            ensure_ascii=True,
        )

        runner.check(
            f"{name}: password not exposed",
            body["password"] not in serialized,
        )


# ==================================================
# 6. MAIN
# ==================================================

def main():

    runner = TestRunner()

    print("=" * 60)
    print("HTTT16 TEXT SECURITY API TEST")
    print("=" * 60)

    test_response_security(runner)

    test_search_security(runner)

    test_request_validation(runner)

    success = runner.summary()

    raise SystemExit(
        0 if success else 1
    )


if __name__ == "__main__":
    main()
