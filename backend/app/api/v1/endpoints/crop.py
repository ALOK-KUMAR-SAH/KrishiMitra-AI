from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.crop_recommendation import (
    CropRecommendationHistoryItem,
    CropRecommendationRequest,
    CropRecommendationResponse,
)
from app.services.crop_recommendation_service import CropRecommendationService
from app.services.farmer_service import get_farmer_profile

router = APIRouter(prefix="/crop", tags=["crop recommendation"])


def _resolve_farmer_profile(current_user: Farmer | None) -> Farmer:
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return current_user


@router.post(
    "/recommend",
    response_model=CropRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Recommend the most suitable crop",
    description="Produces an AI-ready crop recommendation using a mock scoring service and stores the result in history.",
)
def recommend_crop(
    request: CropRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> CropRecommendationResponse:
    farmer = get_farmer_profile(db, current_user.id)
    farmer = _resolve_farmer_profile(farmer)
    service = CropRecommendationService(db)
    return service.recommend(farmer, request)


@router.get(
    "/history",
    response_model=list[CropRecommendationHistoryItem],
    summary="Get recommendation history for the authenticated farmer",
)
def get_crop_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> list[CropRecommendationHistoryItem]:
    farmer = get_farmer_profile(db, current_user.id)
    farmer = _resolve_farmer_profile(farmer)
    service = CropRecommendationService(db)
    return service.get_history(farmer)