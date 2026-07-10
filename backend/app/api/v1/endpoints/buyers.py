from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_buyer
from app.db.database import get_db
from app.models.user import User
from app.schemas.buyer import BuyerCreate, BuyerResponse, BuyerUpdate
from app.services.buyer_service import create_buyer_profile as create_buyer_profile_service
from app.services.buyer_service import get_buyer_profile, update_buyer_profile as update_buyer_profile_service

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.post(
    "/profile",
    response_model=BuyerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create buyer profile",
    description="Creates a buyer profile for the authenticated buyer.",
)
def create_profile(
    buyer_in: BuyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_buyer),
) -> BuyerResponse:
    try:
        return create_buyer_profile_service(db, current_user, buyer_in)
    except ValueError as exc:
        if str(exc) == "buyer_profile_exists":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Buyer profile already exists") from exc
        raise


@router.get(
    "/profile",
    response_model=BuyerResponse,
    summary="Get authenticated buyer profile",
    description="Returns the authenticated buyer's profile.",
)
def read_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_buyer),
) -> BuyerResponse:
    buyer = get_buyer_profile(db, current_user.id)
    if buyer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer profile not found")
    return buyer


@router.put(
    "/profile",
    response_model=BuyerResponse,
    summary="Update buyer profile",
    description="Updates the authenticated buyer's own profile.",
)
def update_profile(
    buyer_in: BuyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_buyer),
) -> BuyerResponse:
    buyer = get_buyer_profile(db, current_user.id)
    if buyer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer profile not found")
    return update_buyer_profile_service(db, buyer, buyer_in)