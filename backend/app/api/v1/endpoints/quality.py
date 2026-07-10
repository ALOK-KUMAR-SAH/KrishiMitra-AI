from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.produce_quality import (
    QualityGradingRequest,
    QualityGradingResponse,
    QualityHistoryResponse,
)
from app.services.farmer_service import get_farmer_profile
from app.services.produce_quality_service import ProduceQualityService

router = APIRouter(prefix="/quality", tags=["produce quality grading"])


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


@router.post(
    "/predict",
    response_model=QualityGradingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grade produce quality from an uploaded image",
    description="Accepts a produce image, stores it under uploads/quality, and returns a deterministic quality grade while saving the result in history.",
)
async def predict_quality(
    crop_name: str = Form(..., description="Crop name for the produce being graded", examples=["Tomato"]),
    image: QualityGradingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> QualityGradingResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = ProduceQualityService(db)
    return await service.grade(farmer, crop_name, image)


@router.get(
    "/history",
    response_model=QualityHistoryResponse,
    summary="Get produce quality history for the authenticated farmer",
)
def get_quality_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> QualityHistoryResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = ProduceQualityService(db)
    return QualityHistoryResponse(items=service.get_history(farmer))