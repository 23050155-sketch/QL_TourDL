
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.tour import Tour
from app.schemas.tour import TourResponse

router = APIRouter(
    prefix="/api/tours",
    tags=["Tours"]
)


@router.get("/", response_model=list[TourResponse])
def get_tours(db: Session = Depends(get_db)):
    tours = (
        db.query(Tour)
        .filter(Tour.status == "active")
        .order_by(Tour.id.desc())
        .all()
    )

    return tours


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
