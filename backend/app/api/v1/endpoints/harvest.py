from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.harvest_prediction import (
    HarvestPredictionHistoryResponse,
    HarvestPredictionRequest,
    HarvestPredictionResponse,
)
from app.services.farmer_service import get_farmer_profile
from app.services.harvest_prediction_service import HarvestPredictionService

router = APIRouter(prefix="/harvest", tags=["harvest prediction"])


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


@router.post(
    "/predict",
    response_model=HarvestPredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict the estimated harvest date",
    description="Uses a placeholder ML-ready service to estimate harvest date and save the prediction history.",
)
def predict_harvest(
    request: HarvestPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> HarvestPredictionResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = HarvestPredictionService(db)
    return service.predict(farmer, request)


@router.get(
    "/history",
    response_model=HarvestPredictionHistoryResponse,
    summary="Get harvest prediction history for the authenticated farmer",
)
def get_harvest_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> HarvestPredictionHistoryResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = HarvestPredictionService(db)
    return HarvestPredictionHistoryResponse(items=service.get_history(farmer))