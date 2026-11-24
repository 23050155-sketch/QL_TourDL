
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# Thống kê tổng quan
class DashboardOverview(BaseModel):
    total_revenue: Decimal

    total_customers: int

    total_tours: int
    active_tours: int

    total_bookings: int
    pending_bookings: int
    completed_bookings: int

    total_guides: int
    total_destinations: int

    total_reviews: int
    average_rating: float


# Thống kê trạng thái đơn đặt Tour
class BookingStatusSummary(BaseModel):
    pending: int
    awaiting_payment: int
    paid: int
    completed: int
    rejected: int
    cancelled: int


# Thống kê doanh thu theo tháng
class MonthlyRevenue(BaseModel):
    year: int
    month: int
    revenue: Decimal
    total_payments: int


# Thống kê Tour được đặt nhiều nhất
class TopTour(BaseModel):
    tour_id: int
    title: str
    total_bookings: int
    total_customers: int


# Danh sách đơn đặt Tour gần đây
class RecentBooking(BaseModel):
    booking_id: int
    customer_name: str
    tour_title: str
    number_of_people: int
    total_amount: Decimal
    status: str
    created_at: datetime | None = None
