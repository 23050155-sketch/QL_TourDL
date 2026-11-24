
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from getpass import getpass


BASE_URL = "http://127.0.0.1:8001"
SCHEDULE_ID = 3

TOKEN = getpass("Nhap access token CUSTOMER: ").strip()

barrier = Barrier(2)


def create_booking(index):
    payload = {
        "schedule_id": SCHEDULE_ID,
        "number_of_people": 1,
        "passengers": [
            {
                "full_name": f"Khach Dong Thoi {index}",
                "date_of_birth": "2000-01-01",
                "phone": "0900000000"
            }
        ]
    }

    request = Request(
        url=f"{BASE_URL}/api/bookings/",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    # Chờ cả hai luồng sẵn sàng
    barrier.wait(timeout=10)

    try:
        with urlopen(request, timeout=30) as response:
            return (
                index,
                response.status,
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        return (
            index,
            error.code,
            error.read().decode("utf-8")
        )


with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(
        executor.map(create_booking, [1, 2])
    )


for index, status_code, body in results:
    print(f"\nYeu cau {index}")
    print(f"HTTP Status: {status_code}")
    print(f"Response: {body}")


codes = sorted(
    result[1] for result in results
)

if codes == [201, 409]:
    print("\nPASS: Khong dat vuot suc chua")
else:
    print("\nFAIL: Can kiem tra lai Backend")
