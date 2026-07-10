from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.user import User
from app.schemas.farmer import FarmerCreate, FarmerResponse, FarmerUpdate
from app.services.farmer_service import create_farmer_profile as create_farmer_profile_service
from app.services.farmer_service import get_farmer_profile, update_farmer_profile as update_farmer_profile_service

router = APIRouter(prefix="/farmers", tags=["farmers"])


@router.post(
    "/profile",
    response_model=FarmerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or replace the authenticated farmer profile",
)
def create_farmer_profile(
    farmer_in: FarmerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> FarmerResponse:
    existing_profile = get_farmer_profile(db, current_user.id)
    if existing_profile is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Farmer profile already exists")
    return create_farmer_profile_service(db, current_user, farmer_in)


@router.get(
    "/profile",
    response_model=FarmerResponse,
    summary="Get the authenticated farmer profile",
)
def read_farmer_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> FarmerResponse:
    farmer = get_farmer_profile(db, current_user.id)
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


@router.put(
    "/profile",
    response_model=FarmerResponse,
    summary="Update the authenticated farmer profile",
)
def update_farmer_profile(
    farmer_in: FarmerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> FarmerResponse:
    farmer = get_farmer_profile(db, current_user.id)
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return update_farmer_profile_service(db, farmer, farmer_in)