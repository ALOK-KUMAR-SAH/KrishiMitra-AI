from fastapi import APIRouter, Depends, HTTPException, status, Form
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

router = APIRouter(
    prefix="/quality",
    tags=["Produce Quality"],
)


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found",
        )
    return farmer


@router.post(
    "/predict",
    response_model=QualityGradingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict Produce Quality",
)
async def predict_quality(
    image: QualityGradingRequest,
    crop_name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
):
    farmer = _resolve_farmer_profile(
        get_farmer_profile(db, current_user.id)
    )

    service = ProduceQualityService(db)

    return await service.grade(
        farmer=farmer,
        crop_name=crop_name,
        image=image,
    )


@router.get(
    "/history",
    response_model=QualityHistoryResponse,
    summary="Get Quality Prediction History",
)
def get_quality_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
):
    farmer = _resolve_farmer_profile(
        get_farmer_profile(db, current_user.id)
    )

    service = ProduceQualityService(db)

    return QualityHistoryResponse(
        items=service.get_history(farmer)
    )