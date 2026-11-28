
import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from getpass import getpass

from sqlalchemy import create_engine, select, func, text

from app.database import engine, SessionLocal
from app.core.security import hash_password

from app.models.user import User
from app.models.tour import Tour
from app.models.destination import Destination, TourDestination
from app.models.tour_schedule import TourSchedule
from app.models.guide import TourGuide, GuideAssignment
from app.models.booking import Booking, BookingPassenger
from app.models.payment import Payment
from app.models.review import Review


# ==================================================
# 1. CONFIGURATION
# ==================================================

ALLOWED_DATABASES = {
    "quan_ly_tour_du_lich",
    "quan_ly_tour_du_lich_test",
}

MODELS = (
    User,
    Destination,
    Tour,
    TourDestination,
    TourSchedule,
    TourGuide,
    GuideAssignment,
    Booking,
    BookingPassenger,
    Payment,
    Review,
)

EXPECTED_COUNTS = {
    "users": 11,
    "destinations": 20,
    "tours": 15,
    "tour_destinations": 45,
    "tour_schedules": 30,
    "tour_guides": 10,
    "guide_assignments": 20,
    "bookings": 40,
    "booking_passengers": 100,
    "payments": 25,
    "reviews": 8,
}


# ==================================================
# 2. DESTINATION DATA
# ==================================================

DESTINATION_DATA = [
    ("Hồ Xuân Hương", "Lâm Đồng"),
    ("Thung lũng Tình Yêu", "Lâm Đồng"),
    ("Quảng trường Lâm Viên", "Lâm Đồng"),
    ("Bãi Sao", "An Giang"),
    ("Dinh Cậu", "An Giang"),
    ("Grand World Phú Quốc", "An Giang"),
    ("Bà Nà Hills", "Đà Nẵng"),
    ("Phố cổ Hội An", "Đà Nẵng"),
    ("Biển Mỹ Khê", "Đà Nẵng"),
    ("Tháp Bà Ponagar", "Khánh Hòa"),
    ("Vịnh Nha Trang", "Khánh Hòa"),
    ("Hồ Hoàn Kiếm", "Hà Nội"),
    ("Vịnh Hạ Long", "Quảng Ninh"),
    ("Fansipan", "Lào Cai"),
    ("Đại Nội Huế", "Huế"),
    ("Kỳ Co", "Gia Lai"),
    ("Đồi cát Mũi Né", "Lâm Đồng"),
    ("Chợ nổi Cái Răng", "Cần Thơ"),
    ("Tràng An", "Ninh Bình"),
    ("Động Phong Nha", "Quảng Trị"),
]


# ==================================================
# 3. TOUR DATA
# ==================================================

# Tên tour, số ngày, số đêm, giá, danh sách địa điểm
TOUR_DATA = [
    (
        "Đà Lạt - Thành phố ngàn hoa",
        3, 2, 2490000, [0, 1, 2]
    ),
    (
        "Phú Quốc - Đảo ngọc",
        4, 3, 4590000, [3, 4, 5]
    ),
    (
        "Đà Nẵng - Hội An",
        4, 3, 3990000, [6, 7, 8]
    ),
    (
        "Nha Trang - Biển xanh",
        3, 2, 2990000, [9, 10]
    ),
    (
        "Hà Nội - Hạ Long",
        5, 4, 5490000, [11, 12, 18]
    ),
    (
        "Hà Nội - Sa Pa",
        4, 3, 4290000, [11, 13]
    ),
    (
        "Huế - Đà Nẵng",
        3, 2, 2790000, [14, 6, 8]
    ),
    (
        "Quy Nhơn - Nha Trang",
        4, 3, 3590000, [15, 9, 10]
    ),
    (
        "Mũi Né - Đà Lạt",
        4, 3, 3690000, [16, 0, 1, 2]
    ),
    (
        "Cần Thơ - Phú Quốc",
        5, 4, 5590000, [17, 3, 4, 5]
    ),
    (
        "Khám phá Đà Lạt",
        2, 1, 1490000, [0, 1, 2]
    ),
    (
        "Hà Nội - Sa Pa - Hạ Long",
        5, 4, 5290000, [11, 13, 12]
    ),
    (
        "Ninh Bình - Hà Nội",
        3, 2, 2890000, [18, 11]
    ),
    (
        "Phong Nha - Huế - Đà Nẵng",
        5, 4, 5890000, [19, 14, 6, 8]
    ),
    (
        "Hội An - Huế",
        3, 2, 2690000, [7, 14, 6]
    ),
]


# ==================================================
# 4. DATABASE SAFETY
# ==================================================

def get_table_counts(db):
    counts = {}

    for model in MODELS:
        counts[model.__tablename__] = db.scalar(
            select(func.count()).select_from(model)
        )

    return counts


def ensure_empty_database(db):
    counts = get_table_counts(db)

    non_empty = {
        table: count
        for table, count in counts.items()
        if count > 0
    }

    if non_empty:
        print("\nDatabase đã có dữ liệu:")

        for table, count in non_empty.items():
            print(f"  {table}: {count}")

        raise ValueError(
            "Script chỉ được chạy trên Database trống."
        )


# ==================================================
# 5. CREATE USERS
# ==================================================

def seed_users(db, password):
    users = []

    admin = User(
        full_name="Quản trị viên Demo",
        email="admin@example.com",
        password_hash=hash_password(password),
        phone=None,
        role="admin",
        status="active",
        token_version=1,
    )

    users.append(admin)

    for index in range(1, 11):
        customer = User(
            full_name=f"Khách hàng Demo {index:02d}",
            email=f"customer{index:02d}@example.com",
            password_hash=hash_password(password),
            phone=None,
            role="customer",
            status="active" if index < 10 else "inactive",
            token_version=1,
        )

        users.append(customer)

    db.add_all(users)
    db.flush()

    print(f"[OK] Users: {len(users)}")

    return users


# ==================================================
# 6. CREATE DESTINATIONS
# ==================================================

def seed_destinations(db):
    destinations = []

    for name, province in DESTINATION_DATA:
        destination = Destination(
            name=name,
            province=province,
            description=(
                f"Khám phá {name} và trải nghiệm "
                "văn hóa, cảnh quan địa phương."
            ),
            image_url=None,
        )

        destinations.append(destination)

    db.add_all(destinations)
    db.flush()

    print(f"[OK] Destinations: {len(destinations)}")

    return destinations


# ==================================================
# 7. CREATE TOURS
# ==================================================

def seed_tours(db):
    tours = []

    for index, data in enumerate(TOUR_DATA):
        title, days, nights, price, _ = data

        tour = Tour(
            title=title,
            description=(
                f"Chương trình du lịch {title}, "
                f"thời gian {days} ngày {nights} đêm. "
                "Dữ liệu giả lập phục vụ kiểm thử hệ thống."
            ),
            duration_days=days,
            duration_nights=nights,
            base_price=Decimal(price),
            image_url=None,
            status="active" if index < 13 else "inactive",
        )

        tours.append(tour)

    db.add_all(tours)
    db.flush()

    print(f"[OK] Tours: {len(tours)}")

    return tours


# ==================================================
# 8. CREATE TOUR DESTINATIONS
# ==================================================

def seed_tour_destinations(db, tours, destinations):
    records = []

    for tour, data in zip(tours, TOUR_DATA):
        destination_indexes = data[4]

        for order, destination_index in enumerate(
            destination_indexes,
            start=1,
        ):
            record = TourDestination(
                tour_id=tour.id,
                destination_id=destinations[
                    destination_index
                ].id,
                visit_order=order,
            )

            records.append(record)

    db.add_all(records)
    db.flush()

    print(f"[OK] Tour destinations: {len(records)}")


# ==================================================
# 9. CREATE TOUR SCHEDULES
# ==================================================

def seed_schedules(db, tours):
    today = date.today()

    past_schedules = []
    future_schedules = []
    cancelled_schedules = []

    # 10 lịch đã kết thúc
    for index in range(10):
        tour = tours[index]

        departure = today - timedelta(
            days=15 + index * 30
        )

        schedule = TourSchedule(
            tour_id=tour.id,
            departure_date=departure,
            return_date=departure + timedelta(
                days=tour.duration_days - 1
            ),
            capacity=30,
            status="closed",
        )

        past_schedules.append(schedule)

    # 18 lịch khởi hành tương lai
    for index in range(18):
        tour = tours[index % 13]

        departure = today + timedelta(
            days=7 + index * 4
        )

        schedule = TourSchedule(
            tour_id=tour.id,
            departure_date=departure,
            return_date=departure + timedelta(
                days=tour.duration_days - 1
            ),
            capacity=30,
            status="open",
        )

        future_schedules.append(schedule)

    # 2 lịch đã hủy
    for index in range(2):
        tour = tours[13 + index]

        departure = today + timedelta(
            days=30 + index * 7
        )

        schedule = TourSchedule(
            tour_id=tour.id,
            departure_date=departure,
            return_date=departure + timedelta(
                days=tour.duration_days - 1
            ),
            capacity=20,
            status="cancelled",
        )

        cancelled_schedules.append(schedule)

    schedules = (
        past_schedules
        + future_schedules
        + cancelled_schedules
    )

    db.add_all(schedules)
    db.flush()

    print(f"[OK] Tour schedules: {len(schedules)}")

    return past_schedules, future_schedules


# ==================================================
# 10. CREATE TOUR GUIDES
# ==================================================

def seed_guides(db):
    guides = []

    for index in range(1, 11):
        guide = TourGuide(
            full_name=f"Hướng dẫn viên Demo {index:02d}",
            email=f"guide{index:02d}@example.com",
            phone=None,
            experience_years=index + 1,
            status="active" if index < 10 else "inactive",
        )

        guides.append(guide)

    db.add_all(guides)
    db.flush()

    print(f"[OK] Tour guides: {len(guides)}")

    return guides


# ==================================================
# 11. CREATE GUIDE ASSIGNMENTS
# ==================================================

def seed_guide_assignments(
    db,
    guides,
    past_schedules,
    future_schedules,
):
    assignments = []

    schedules = (
        past_schedules
        + future_schedules[:10]
    )

    active_guides = guides[:9]

    for index, schedule in enumerate(schedules):
        guide = active_guides[
            index % len(active_guides)
        ]

        assignment = GuideAssignment(
            schedule_id=schedule.id,
            guide_id=guide.id,
            assigned_at=datetime.combine(
                schedule.departure_date
                - timedelta(days=7),
                datetime.min.time(),
            ),
        )

        assignments.append(assignment)

    db.add_all(assignments)
    db.flush()

    print(f"[OK] Guide assignments: {len(assignments)}")


# ==================================================
# 12. CREATE BOOKINGS AND PASSENGERS
# ==================================================

def seed_bookings(
    db,
    users,
    tours,
    past_schedules,
    future_schedules,
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    customers = users[1:10]

    tour_map = {
        tour.id: tour
        for tour in tours
    }

    statuses = (
        ["pending"] * 8
        + ["awaiting_payment"] * 7
        + ["paid"] * 10
        + ["completed"] * 8
        + ["cancelled"] * 4
        + ["rejected"] * 3
    )

    bookings = []
    completed_index = 0
    passenger_count = 0

    for index, status in enumerate(statuses):
        customer = customers[
            index % len(customers)
        ]

        if status == "completed":
            schedule = past_schedules[completed_index]
            completed_index += 1

            created_at = datetime.combine(
                schedule.departure_date
                - timedelta(days=14),
                datetime.min.time(),
            )
        else:
            schedule = future_schedules[
                index % len(future_schedules)
            ]

            created_at = now - timedelta(
                days=2 + index % 5
            )

        tour = tour_map[schedule.tour_id]

        number_of_people = 2 + index % 2

        unit_price = Decimal(tour.base_price)

        total_amount = (
            unit_price * number_of_people
        )

        booking = Booking(
            user_id=customer.id,
            schedule_id=schedule.id,
            number_of_people=number_of_people,
            unit_price=unit_price,
            total_amount=total_amount,
            status=status,
            created_at=created_at,
        )

        for passenger_index in range(
            number_of_people
        ):
            passenger = BookingPassenger(
                full_name=(
                    f"Hành khách Demo "
                    f"{index + 1:02d}-"
                    f"{passenger_index + 1:02d}"
                ),
                date_of_birth=date(
                    1990 + passenger_index,
                    1,
                    15,
                ),
                phone=None,
            )

            booking.passengers.append(passenger)
            passenger_count += 1

        bookings.append(booking)

    db.add_all(bookings)
    db.flush()

    print(f"[OK] Bookings: {len(bookings)}")
    print(f"[OK] Booking passengers: {passenger_count}")

    return bookings


# ==================================================
# 13. CREATE PAYMENTS
# ==================================================

def seed_payments(db, bookings):
    payments = []

    pending_count = 0
    failed_count = 0

    methods = [
        "cash",
        "bank_transfer",
        "online",
    ]

    for index, booking in enumerate(bookings):
        payment_status = None

        if booking.status in (
            "paid",
            "completed",
        ):
            payment_status = "success"

        elif booking.status == "awaiting_payment":
            if pending_count < 5:
                payment_status = "pending"
                pending_count += 1

        elif booking.status == "cancelled":
            if failed_count < 2:
                payment_status = "failed"
                failed_count += 1

        if payment_status is None:
            continue

        created_at = (
            booking.created_at + timedelta(hours=1)
        )

        paid_at = None

        if payment_status == "success":
            paid_at = created_at + timedelta(hours=1)

        payment = Payment(
            booking_id=booking.id,
            amount=Decimal(booking.total_amount),
            payment_method=methods[
                index % len(methods)
            ],
            status=payment_status,
            transaction_code=f"DEMO-PAY-{index + 1:04d}",
            paid_at=paid_at,
            created_at=created_at,
        )

        payments.append(payment)

    db.add_all(payments)
    db.flush()

    print(f"[OK] Payments: {len(payments)}")


# ==================================================
# 14. CREATE REVIEWS
# ==================================================

def seed_reviews(db, bookings, past_schedules):
    comments = [
        "Chuyến đi rất thú vị.",
        "Lịch trình hợp lý và dịch vụ tốt.",
        "Hướng dẫn viên nhiệt tình.",
        "Cảnh quan đẹp, trải nghiệm đáng nhớ.",
        "Dịch vụ khá tốt.",
        "Tour được tổ chức chuyên nghiệp.",
        "Rất hài lòng với chuyến đi.",
        "Một trải nghiệm du lịch tuyệt vời.",
    ]

    schedule_map = {
        schedule.id: schedule
        for schedule in past_schedules
    }

    reviews = []

    for booking in bookings:
        if booking.status != "completed":
            continue

        schedule = schedule_map[
            booking.schedule_id
        ]

        index = len(reviews)

        review = Review(
            user_id=booking.user_id,
            tour_id=schedule.tour_id,
            rating=[5, 4, 5, 4, 3, 5, 4, 5][index],
            comment=comments[index],
            created_at=datetime.combine(
                schedule.return_date
                + timedelta(days=1),
                datetime.min.time(),
            ),
        )

        reviews.append(review)

    db.add_all(reviews)
    db.flush()

    print(f"[OK] Reviews: {len(reviews)}")


# ==================================================
# 15. VALIDATE DATA
# ==================================================

def validate_seed_data(db):
    actual_counts = get_table_counts(db)

    for table, expected in EXPECTED_COUNTS.items():
        actual = actual_counts[table]

        if actual != expected:
            raise ValueError(
                f"{table}: expected={expected}, "
                f"actual={actual}"
            )

    bookings = db.scalars(
        select(Booking)
    ).all()

    schedules = {
        schedule.id: schedule
        for schedule in db.scalars(
            select(TourSchedule)
        ).all()
    }

    payments = db.scalars(
        select(Payment)
    ).all()

    payment_map = {}

    for payment in payments:
        payment_map.setdefault(
            payment.booking_id, []
        ).append(payment)

    occupied = Counter()
    completed_pairs = set()

    for booking in bookings:
        schedule = schedules[
            booking.schedule_id
        ]

        if len(booking.passengers) != (
            booking.number_of_people
        ):
            raise ValueError(
                "Số lượng hành khách không hợp lệ."
            )

        expected_amount = (
            booking.unit_price
            * booking.number_of_people
        )

        if booking.total_amount != expected_amount:
            raise ValueError(
                "Tổng tiền Booking không hợp lệ."
            )

        booking_payments = payment_map.get(
            booking.id, []
        )

        for payment in booking_payments:
            if payment.amount != booking.total_amount:
                raise ValueError(
                    "Số tiền Payment không hợp lệ."
                )

        active_payments = [
            payment
            for payment in booking_payments
            if payment.status in ("pending", "success")
        ]

        if len(active_payments) > 1:
            raise ValueError(
                "Booking có Payment bị trùng."
            )

        allowed_payment_statuses = {
            "pending": set(),
            "awaiting_payment": {"pending"},
            "paid": {"success"},
            "completed": {"success"},
            "cancelled": {"failed"},
            "rejected": set(),
        }

        if any(
            payment.status not in
            allowed_payment_statuses[booking.status]
            for payment in booking_payments
        ):
            raise ValueError(
                "Trạng thái Payment không phù hợp."
            )

        if booking.status in (
            "paid",
            "completed",
        ):
            if not any(
                payment.status == "success"
                for payment in booking_payments
            ):
                raise ValueError(
                    "Booking thiếu Payment thành công."
                )

        if booking.status in (
            "pending",
            "awaiting_payment",
            "paid",
            "completed",
        ):
            occupied[booking.schedule_id] += (
                booking.number_of_people
            )

        if booking.status == "completed":
            if schedule.return_date > date.today():
                raise ValueError(
                    "Booking hoàn thành sai thời điểm."
                )

            completed_pairs.add(
                (booking.user_id, schedule.tour_id)
            )

    for schedule_id, count in occupied.items():
        if count > schedules[schedule_id].capacity:
            raise ValueError(
                "Lịch khởi hành vượt quá sức chứa."
            )

    for schedule in schedules.values():
        if schedule.return_date < schedule.departure_date:
            raise ValueError(
                "Ngày kết thúc không hợp lệ."
            )

    reviews = db.scalars(
        select(Review)
    ).all()

    review_pairs = set()

    for review in reviews:
        pair = (
            review.user_id,
            review.tour_id,
        )

        if pair not in completed_pairs:
            raise ValueError(
                "Review không có Booking hoàn thành."
            )

        if pair in review_pairs:
            raise ValueError(
                "Review bị trùng."
            )

        if not 1 <= review.rating <= 5:
            raise ValueError(
                "Rating không hợp lệ."
            )

        review_pairs.add(pair)

    assignments = db.scalars(
        select(GuideAssignment)
    ).all()

    guide_map = {}

    for assignment in assignments:
        guide_map.setdefault(
            assignment.guide_id, []
        ).append(
            schedules[assignment.schedule_id]
        )

    for guide_schedules in guide_map.values():
        ordered = sorted(
            guide_schedules,
            key=lambda item: item.departure_date,
        )

        for previous, current in zip(
            ordered,
            ordered[1:],
        ):
            if (
                current.departure_date
                <= previous.return_date
            ):
                raise ValueError(
                    "Hướng dẫn viên bị trùng lịch."
                )

    print("[OK] Data consistency validation")


# ==================================================
# 16. PRINT SUMMARY
# ==================================================

def print_summary(db):
    counts = get_table_counts(db)

    print("\n" + "=" * 55)
    print("DEMO DATA SUMMARY")
    print("=" * 55)

    for table, count in counts.items():
        print(f"{table:<25}: {count:>5}")

    print("-" * 55)
    print(f"{'TOTAL RECORDS':<25}: {sum(counts.values()):>5}")
    print("=" * 55)


# ==================================================
# 17. MAIN FUNCTION
# ==================================================

def main():
    parser = argparse.ArgumentParser(
        description="HTTT16 Demo Data Seeder"
    )

    parser.add_argument(
        "--database",
        required=True,
        choices=sorted(ALLOWED_DATABASES),
        help="Tên Database local cần tạo dữ liệu mẫu",
    )

    args = parser.parse_args()

    if engine.url.host not in (
        "127.0.0.1",
        "localhost",
        "::1",
    ):
        print("[ERROR] Chỉ hỗ trợ MySQL local.")
        return 1

    seed_engine = create_engine(
        engine.url.set(database=args.database),
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={
            "init_command": "SET SESSION time_zone = '+00:00'"
        },
    )

    try:
        with SessionLocal(bind=seed_engine) as db:
            database_name = db.scalar(
                text("SELECT DATABASE()")
            )

            print("=" * 55)
            print("HTTT16 - DEMO DATA SEEDER")
            print("=" * 55)
            print(f"Database: {database_name}")
            print(f"Host: {seed_engine.url.host}")

            if database_name != args.database:
                raise ValueError(
                    "Database không đúng mục tiêu."
                )

            ensure_empty_database(db)

            confirmation = input(
                f"\nNhập {database_name} để xác nhận: "
            ).strip()

            if confirmation != database_name:
                print("Đã hủy thao tác.")
                return 0

            password = getpass(
                "Nhập mật khẩu cho các tài khoản Demo: "
            )

            confirm_password = getpass(
                "Nhập lại mật khẩu: "
            )

            if password != confirm_password:
                raise ValueError(
                    "Mật khẩu xác nhận không khớp."
                )

            if not 8 <= len(password) <= 128:
                raise ValueError(
                    "Mật khẩu phải có từ 8 đến 128 ký tự."
                )

            print("\nĐang khởi tạo dữ liệu mẫu...\n")

            users = seed_users(db, password)

            destinations = seed_destinations(db)

            tours = seed_tours(db)

            seed_tour_destinations(
                db,
                tours,
                destinations,
            )

            past_schedules, future_schedules = (
                seed_schedules(db, tours)
            )

            guides = seed_guides(db)

            seed_guide_assignments(
                db,
                guides,
                past_schedules,
                future_schedules,
            )

            bookings = seed_bookings(
                db,
                users,
                tours,
                past_schedules,
                future_schedules,
            )

            seed_payments(db, bookings)

            seed_reviews(
                db,
                bookings,
                past_schedules,
            )

            validate_seed_data(db)

            print_summary(db)

            db.commit()

            print("\n[SUCCESS] Tạo dữ liệu mẫu thành công.")
            print("Admin: admin@example.com")
            print("Customer: customer01@example.com")
            print("Mật khẩu: mật khẩu Demo vừa nhập.")

            return 0

    except KeyboardInterrupt:
        print("\n[CANCELLED] Đã hủy thao tác.")
        return 1

    except ValueError as exc:
        print(f"\n[ERROR] {exc}")
        print("Không Commit dữ liệu.")
        return 1

    except Exception as exc:
        print(
            f"\n[ERROR] {type(exc).__name__}"
        )
        print("Transaction không hoàn tất.")
        return 1

    finally:
        seed_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
