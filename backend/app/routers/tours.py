
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, select

from app.database import get_db
from app.models.tour import Tour
from app.models.user import User
from app.models.tour_schedule import TourSchedule
from app.models.destination import Destination, TourDestination
from app.models.review import Review

from app.schemas.tour import (
    TourCreate,
    TourUpdate,
    TourResponse,
    TourSearchItem,
    TourSearchResponse
)
from app.schemas.tour_schedule import TourScheduleResponse


from app.routers.auth import require_admin

from app.services.availability import enrich_schedules

from datetime import date
from decimal import Decimal
from typing import Literal



from app.core.validation import (
    MAX_SEARCH_LENGTH,
    MAX_PROVINCE_LENGTH,
    MAX_TOUR_DURATION_DAYS,
    MAX_TOUR_PRICE,
    MAX_PAGE_SIZE,
    MAX_PAGE_NUMBER,
)

from app.core.search_validation import (
    normalize_search_keyword,
    validate_price_range,
    validate_pagination,
    calculate_total_pages,
)






router = APIRouter(
    prefix="/api/tours",
    tags=["Tours"]
)


# Lấy danh sách tour đang hoạt động cho khách hàng
@router.get("/", response_model=list[TourResponse])
def get_tours(db: Session = Depends(get_db)):
    return (
        db.query(Tour)
        .filter(Tour.status == "active")
        .order_by(Tour.id.desc())
        .all()
    )


# ADMIN lấy toàn bộ tour, bao gồm tour đã ngừng kinh doanh
@router.get("/admin/all", response_model=list[TourResponse])
def get_all_tours(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return db.query(Tour).order_by(Tour.id.desc()).all()



# Tìm kiếm, lọc và phân trang Tour

@router.get(
    "/search",
    response_model=TourSearchResponse
)
def search_tours(
    search: str | None = Query(
        default=None,
        max_length=MAX_SEARCH_LENGTH
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
        le=MAX_TOUR_PRICE
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
        le=MAX_TOUR_PRICE
    ),
    duration_days: int | None = Query(
        default=None,
        ge=1,
        le=MAX_TOUR_DURATION_DAYS
    ),
    province: str | None = Query(
        default=None,
        max_length=MAX_PROVINCE_LENGTH
    ),
    sort_by: Literal[
        "newest",
        "oldest",
        "price_asc",
        "price_desc",
        "duration_asc",
        "duration_desc"
    ] = "newest",
    page: int = Query(
        default=1,
        ge=1,
        le=MAX_PAGE_NUMBER
    ),
    page_size: int = Query(
        default=12,
        ge=1,
        le=MAX_PAGE_SIZE
    ),
    db: Session = Depends(get_db)
):

    # 1. Kiểm tra phân trang
    offset = validate_pagination(
        page,
        page_size
    )

    # Kiểm tra và chuẩn hóa tham số tìm kiếm
    min_price, max_price = validate_price_range(
        min_price,
        max_price,
    )

    keyword = normalize_search_keyword(
        search,
        max_length=MAX_SEARCH_LENGTH
    )

    province_keyword = normalize_search_keyword(
        province,
        max_length=MAX_PROVINCE_LENGTH
    )

    # 2. Chỉ lấy Tour đang hoạt động
    query = db.query(Tour).filter(
        Tour.status == "active"
    )

    
    # 3. Tìm kiếm theo tên và mô tả Tour
    if keyword is not None:
        query = query.filter(
            or_(
                Tour.title.contains(
                    keyword,
                    autoescape=True
                ),
                Tour.description.contains(
                    keyword,
                    autoescape=True
                )
            )
        )


    # 4. Lọc theo khoảng giá
    if min_price is not None:
        query = query.filter(
            Tour.base_price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Tour.base_price <= max_price
        )

    # 5. Lọc theo số ngày
    if duration_days is not None:
        query = query.filter(
            Tour.duration_days == duration_days
        )

    
    # 6. Lọc theo tỉnh/thành phố
    if province_keyword is not None:

        destination_tour_ids = (
            select(TourDestination.tour_id)
            .join(
                Destination,
                TourDestination.destination_id
                == Destination.id
            )
            .where(
                Destination.province.contains(
                    province_keyword,
                    autoescape=True
                )
            )
        )

        query = query.filter(
            Tour.id.in_(destination_tour_ids)
        )


    # 7. Đếm tổng số Tour sau khi lọc
    total = query.count()

    total_pages = calculate_total_pages(
        total,
        page_size
    )

    # 8. Truy vấn thống kê đánh giá
    review_stats = (
        db.query(
            Review.tour_id.label("tour_id"),
            func.avg(
                Review.rating
            ).label("average_rating"),
            func.count(
                Review.id
            ).label("total_reviews")
        )
        .group_by(Review.tour_id)
        .subquery()
    )

    # Kết hợp Tour với thống kê đánh giá
    query = (
        query
        .outerjoin(
            review_stats,
            Tour.id == review_stats.c.tour_id
        )
        .add_columns(
            func.coalesce(
                review_stats.c.average_rating, 0
            ).label("average_rating"),

            func.coalesce(
                review_stats.c.total_reviews, 0
            ).label("total_reviews")
        )
    )

    # 9. Sắp xếp kết quả
    sort_options = {
        "newest": Tour.id.desc(),
        "oldest": Tour.id.asc(),
        "price_asc": Tour.base_price.asc(),
        "price_desc": Tour.base_price.desc(),
        "duration_asc": Tour.duration_days.asc(),
        "duration_desc": Tour.duration_days.desc()
    }

    query = query.order_by(
        sort_options[sort_by],
        Tour.id.desc()
    )

    # 10. Phân trang
    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 11. Chuẩn hóa dữ liệu trả về
    items = []

    for tour, average_rating, total_reviews in rows:
        tour_data = (
            TourResponse
            .model_validate(tour)
            .model_dump()
        )

        items.append(
            TourSearchItem(
                **tour_data,
                average_rating=round(
                    float(average_rating), 2
                ),
                total_reviews=int(total_reviews)
            )
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items
    }



# Xem thông tin chi tiết tour đang hoạt động
@router.get("/{tour_id}", response_model=TourResponse)
def get_tour_detail(
    tour_id: int,
    db: Session = Depends(get_db)
):
    tour = (
        db.query(Tour)
        .filter(
            Tour.id == tour_id,
            Tour.status == "active"
        )
        .first()
    )

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    return tour


# ADMIN tạo tour mới
@router.post(
    "/",
    response_model=TourResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tour(
    data: TourCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = Tour(**data.model_dump(), status="active")

    db.add(tour)
    db.commit()
    db.refresh(tour)

    return tour


# ADMIN cập nhật thông tin tour
@router.put("/{tour_id}", response_model=TourResponse)
def update_tour(
    tour_id: int,
    data: TourUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    for field, value in data.model_dump().items():
        setattr(tour, field, value)

    db.commit()
    db.refresh(tour)

    return tour


# ADMIN ngừng kinh doanh tour bằng cách cập nhật trạng thái
@router.delete("/{tour_id}")
def delete_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tour"
        )

    tour.status = "inactive"
    db.commit()

    return {"message": "Đã ngừng kinh doanh tour thành công"}







# Lấy lịch khởi hành đang mở của một Tour
@router.get(
    "/{tour_id}/departures",
    response_model=list[TourScheduleResponse]
)
def get_tour_departures(
    tour_id: int,
    db: Session = Depends(get_db)
):
    tour = db.get(Tour, tour_id)

    if not tour or tour.status != "active":
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour đang hoạt động"
        )

    schedules = (
        db.query(TourSchedule)
        .filter(
            TourSchedule.tour_id == tour_id,
            TourSchedule.status == "open",
            TourSchedule.departure_date >= date.today()
        )
        .order_by(TourSchedule.departure_date.asc())
        .all()
    )

    return enrich_schedules(db, schedules)


