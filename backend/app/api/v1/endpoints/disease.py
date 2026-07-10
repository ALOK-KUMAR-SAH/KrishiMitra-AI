from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.disease_detection import (
    DiseaseDetectionHistoryItem,
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
)
from app.services.disease_detection_service import DiseaseDetectionService
from app.services.farmer_service import get_farmer_profile

router = APIRouter(prefix="/disease", tags=["disease detection"])


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


@router.post(
    "/predict",
    response_model=DiseaseDetectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Detect crop disease from an image",
    description="Accepts a crop image upload, stores it in uploads/, creates a history record, and returns the predicted disease with a recommended solution.",
)
async def predict_disease(
    image: DiseaseDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> DiseaseDetectionResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = DiseaseDetectionService(db)
    return await service.predict(farmer, image)


@router.get(
    "/history",
    response_model=list[DiseaseDetectionHistoryItem],
    summary="Get disease detection history for the authenticated farmer",
)
def get_disease_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> list[DiseaseDetectionHistoryItem]:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = DiseaseDetectionService(db)
    return service.get_history(farmer)