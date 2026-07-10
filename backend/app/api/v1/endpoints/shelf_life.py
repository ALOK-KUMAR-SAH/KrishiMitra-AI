from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.shelf_life_prediction import (
    ShelfLifePredictionHistoryResponse,
    ShelfLifePredictionRequest,
    ShelfLifePredictionResponse,
)
from app.services.farmer_service import get_farmer_profile
from app.services.shelf_life_prediction_service import ShelfLifePredictionService

router = APIRouter(prefix="/shelf-life", tags=["shelf life prediction"])


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


@router.post(
    "/predict",
    response_model=ShelfLifePredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict the remaining shelf life of harvested produce",
    description="Uses a deterministic ML-ready service to estimate shelf life and store the result in history.",
)
def predict_shelf_life(
    request: ShelfLifePredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> ShelfLifePredictionResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = ShelfLifePredictionService(db)
    return service.predict(farmer, request)


@router.get(
    "/history",
    response_model=ShelfLifePredictionHistoryResponse,
    summary="Get shelf-life prediction history for the authenticated farmer",
)
def get_shelf_life_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> ShelfLifePredictionHistoryResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = ShelfLifePredictionService(db)
    return ShelfLifePredictionHistoryResponse(items=service.get_history(farmer))