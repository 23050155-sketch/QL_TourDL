
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User
from app.models.tour import Tour
from app.models.tour_schedule import TourSchedule
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.destination import Destination
from app.models.guide import TourGuide
from app.models.review import Review

from app.routers.auth import require_admin

from app.schemas.dashboard import (
    DashboardOverview,
    BookingStatusSummary,
    MonthlyRevenue,
    TopTour,
    RecentBooking,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


# 1. ADMIN xem thống kê tổng quan
@router.get(
    "/overview",
    response_model=DashboardOverview,
)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    # Tổng doanh thu
    total_revenue = (
        db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        )
        .filter(Payment.status == "success")
        .scalar()
    )

    # Tổng khách hàng
    total_customers = (
        db.query(User)
        .filter(User.role == "customer")
        .count()
    )

    # Thống kê Tour
    total_tours = db.query(Tour).count()

    active_tours = (
        db.query(Tour)
        .filter(Tour.status == "active")
        .count()
    )

    # Thống kê đơn đặt Tour
    total_bookings = db.query(Booking).count()

    pending_bookings = (
        db.query(Booking)
        .filter(Booking.status == "pending")
        .count()
    )

    completed_bookings = (
        db.query(Booking)
        .filter(Booking.status == "completed")
        .count()
    )

    # Thống kê hướng dẫn viên và địa điểm
    total_guides = db.query(TourGuide).count()

    total_destinations = db.query(Destination).count()

    # Thống kê đánh giá
    total_reviews = db.query(Review).count()

    average_rating = (
        db.query(
            func.coalesce(func.avg(Review.rating), 0)
        )
        .scalar()
    )

    return {
        "total_revenue": total_revenue,
        "total_customers": total_customers,
        "total_tours": total_tours,
        "active_tours": active_tours,
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "completed_bookings": completed_bookings,
        "total_guides": total_guides,
        "total_destinations": total_destinations,
        "total_reviews": total_reviews,
        "average_rating": round(float(average_rating), 2),
    }


# 2. ADMIN thống kê trạng thái đơn đặt Tour
@router.get(
    "/booking-status",
    response_model=BookingStatusSummary,
)
def get_booking_status(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rows = (
        db.query(
            Booking.status,
            func.count(Booking.id),
        )
        .group_by(Booking.status)
        .all()
    )

    counts = {
        booking_status: total
        for booking_status, total in rows
    }

    return {
        "pending": counts.get("pending", 0),
        "awaiting_payment": counts.get("awaiting_payment", 0),
        "paid": counts.get("paid", 0),
        "completed": counts.get("completed", 0),
        "rejected": counts.get("rejected", 0),
        "cancelled": counts.get("cancelled", 0),
    }


# 3. ADMIN thống kê doanh thu theo tháng
@router.get(
    "/monthly-revenue",
    response_model=list[MonthlyRevenue],
)
def get_monthly_revenue(
    year: int = Query(
        default=date.today().year,
        ge=2000,
        le=2100,
    ),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    month_column = extract("month", Payment.paid_at)

    rows = (
        db.query(
            month_column.label("month"),
            func.sum(Payment.amount).label("revenue"),
            func.count(Payment.id).label("total_payments"),
        )
        .filter(
            Payment.status == "success",
            Payment.paid_at.isnot(None),
            extract("year", Payment.paid_at) == year,
        )
        .group_by(month_column)
        .all()
    )

    monthly_data = {
        int(row.month): {
            "revenue": row.revenue,
            "total_payments": row.total_payments,
        }
        for row in rows
    }

    result = []

    # Luôn trả về đủ 12 tháng
    for month in range(1, 13):
        data = monthly_data.get(
            month,
            {
                "revenue": Decimal("0.00"),
                "total_payments": 0,
            },
        )

        result.append({
            "year": year,
            "month": month,
            "revenue": data["revenue"],
            "total_payments": data["total_payments"],
        })

    return result


# 4. ADMIN xem Tour được đặt nhiều nhất
@router.get(
    "/top-tours",
    response_model=list[TopTour],
)
def get_top_tours(
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rows = (
        db.query(
            Tour.id.label("tour_id"),
            Tour.title.label("title"),
            func.count(Booking.id).label("total_bookings"),
            func.coalesce(
                func.sum(Booking.number_of_people), 0
            ).label("total_customers"),
        )
        .join(
            TourSchedule,
            TourSchedule.tour_id == Tour.id,
        )
        .join(
            Booking,
            Booking.schedule_id == TourSchedule.id,
        )
        .filter(
            Booking.status.in_([
                "paid",
                "completed",
            ])
        )
        .group_by(Tour.id, Tour.title)
        .order_by(
            func.count(Booking.id).desc(),
            Tour.id.asc(),
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "tour_id": row.tour_id,
            "title": row.title,
            "total_bookings": row.total_bookings,
            "total_customers": int(row.total_customers),
        }
        for row in rows
    ]


# 5. ADMIN xem đơn đặt Tour gần đây
@router.get(
    "/recent-bookings",
    response_model=list[RecentBooking],
)
def get_recent_bookings(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    rows = (
        db.query(
            Booking.id.label("booking_id"),
            User.full_name.label("customer_name"),
            Tour.title.label("tour_title"),
            Booking.number_of_people,
            Booking.total_amount,
            Booking.status,
            Booking.created_at,
        )
        .join(
            User,
            Booking.user_id == User.id,
        )
        .join(
            TourSchedule,
            Booking.schedule_id == TourSchedule.id,
        )
        .join(
            Tour,
            TourSchedule.tour_id == Tour.id,
        )
        .order_by(
            Booking.created_at.desc(),
            Booking.id.desc(),
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "booking_id": row.booking_id,
            "customer_name": row.customer_name,
            "tour_title": row.tour_title,
            "number_of_people": row.number_of_people,
            "total_amount": row.total_amount,
            "status": row.status,
            "created_at": row.created_at,
        }
        for row in rows
    ]
