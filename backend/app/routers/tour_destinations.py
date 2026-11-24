
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.destination import Destination, TourDestination
from app.models.tour import Tour
from app.models.user import User
from app.routers.auth import require_admin
from app.schemas.destination import (
    TourDestinationCreate,
    TourDestinationResponse,
)


router = APIRouter(
    prefix="/api/tours",
    tags=["Tour Destinations"],
)


class VisitOrderUpdate(BaseModel):
    visit_order: int = Field(ge=1)



# 1. Xem danh sách địa điểm thuộc Tour đang hoạt động
@router.get("/{tour_id}/destinations")
def get_tour_destinations(
    tour_id: int,
    db: Session = Depends(get_db),
):
    # Chỉ cho phép xem Tour đang hoạt động
    tour = (
        db.query(Tour)
        .filter(
            Tour.id == tour_id,
            Tour.status == "active",
        )
        .first()
    )

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour đang hoạt động",
        )

    rows = (
        db.query(TourDestination, Destination)
        .join(
            Destination,
            TourDestination.destination_id == Destination.id,
        )
        .filter(TourDestination.tour_id == tour_id)
        .order_by(
            TourDestination.visit_order.asc(),
            TourDestination.destination_id.asc(),
        )
        .all()
    )

    return [
        {
            "tour_id": relation.tour_id,
            "destination_id": destination.id,
            "name": destination.name,
            "province": destination.province,
            "description": destination.description,
            "image_url": destination.image_url,
            "visit_order": relation.visit_order,
        }
        for relation, destination in rows
    ]




# ADMIN xem địa điểm của mọi Tour
@router.get("/admin/{tour_id}/destinations")
def admin_get_tour_destinations(
    tour_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour",
        )

    rows = (
        db.query(TourDestination, Destination)
        .join(
            Destination,
            TourDestination.destination_id == Destination.id,
        )
        .filter(TourDestination.tour_id == tour_id)
        .order_by(
            TourDestination.visit_order.asc(),
            TourDestination.destination_id.asc(),
        )
        .all()
    )

    return [
        {
            "tour_id": relation.tour_id,
            "destination_id": destination.id,
            "name": destination.name,
            "province": destination.province,
            "description": destination.description,
            "image_url": destination.image_url,
            "visit_order": relation.visit_order,
        }
        for relation, destination in rows
    ]




# 2. ADMIN thêm địa điểm vào Tour
@router.post(
    "/{tour_id}/destinations",
    response_model=TourDestinationResponse,
    status_code=201,
)
def add_destination_to_tour(
    tour_id: int,
    data: TourDestinationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    tour = db.get(Tour, tour_id)

    if not tour:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy Tour",
        )

    destination = db.get(Destination, data.destination_id)

    if not destination:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy địa điểm",
        )

    existing = db.get(
        TourDestination,
        (tour_id, data.destination_id),
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Địa điểm đã thuộc Tour này",
        )

    relation = TourDestination(
        tour_id=tour_id,
        destination_id=data.destination_id,
        visit_order=data.visit_order,
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)

    return relation


# 3. ADMIN cập nhật thứ tự tham quan
@router.put(
    "/{tour_id}/destinations/{destination_id}",
    response_model=TourDestinationResponse,
)
def update_visit_order(
    tour_id: int,
    destination_id: int,
    data: VisitOrderUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    relation = db.get(
        TourDestination,
        (tour_id, destination_id),
    )

    if not relation:
        raise HTTPException(
            status_code=404,
            detail="Địa điểm không thuộc Tour này",
        )

    relation.visit_order = data.visit_order

    db.commit()
    db.refresh(relation)

    return relation


# 4. ADMIN gỡ địa điểm khỏi Tour
@router.delete(
    "/{tour_id}/destinations/{destination_id}",
)
def remove_destination_from_tour(
    tour_id: int,
    destination_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    relation = db.get(
        TourDestination,
        (tour_id, destination_id),
    )

    if not relation:
        raise HTTPException(
            status_code=404,
            detail="Địa điểm không thuộc Tour này",
        )

    db.delete(relation)
    db.commit()

    return {
        "message": "Gỡ địa điểm khỏi Tour thành công",
        "tour_id": tour_id,
        "destination_id": destination_id,
    }
