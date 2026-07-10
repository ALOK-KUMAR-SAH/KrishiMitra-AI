from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_farmer
from app.db.database import get_db
from app.models.farmer import Farmer
from app.models.marketplace import MarketplaceListing
from app.models.user import User
from app.schemas.marketplace import (
    MarketplaceListingCreate,
    MarketplaceListingResponse,
    MarketplaceListingsResponse,
    MarketplaceListingUpdate,
)
from app.services.farmer_service import get_farmer_profile
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _resolve_farmer_profile(farmer: Farmer | None) -> Farmer:
    if farmer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found")
    return farmer


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")


@router.post(
    "/listings",
    response_model=MarketplaceListingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a produce listing",
    description="Creates a new produce listing for the authenticated farmer.",
)
def create_listing(
    listing_in: MarketplaceListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> MarketplaceListingResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = MarketplaceService(db)
    try:
        return service.create_listing(farmer, listing_in)
    except ValueError as exc:
        detail = "quantity_unit must be one of kg, ton, quintal" if str(exc) == "quantity_unit" else "status must be one of available, reserved, sold"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc


@router.get(
    "/listings",
    response_model=MarketplaceListingsResponse,
    summary="Browse available produce listings",
    description="Public endpoint that returns only listings currently marked as available.",
)
def list_public_listings(db: Session = Depends(get_db)) -> MarketplaceListingsResponse:
    service = MarketplaceService(db)
    return MarketplaceListingsResponse(items=service.get_public_listings())


@router.get(
    "/listings/{listing_id}",
    response_model=MarketplaceListingResponse,
    summary="Get a produce listing by id",
    description="Returns an available listing publicly, or a private listing only to its owning farmer.",
)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
) -> MarketplaceListingResponse:
    service = MarketplaceService(db)
    listing = service.get_listing_by_id(listing_id)
    if listing is None or listing.status != "available":
        raise _not_found()
    return listing


@router.put(
    "/listings/{listing_id}",
    response_model=MarketplaceListingResponse,
    summary="Update a produce listing",
    description="Updates a listing owned by the authenticated farmer.",
)
def update_listing(
    listing_id: int,
    listing_in: MarketplaceListingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> MarketplaceListingResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = MarketplaceService(db)
    listing = service.get_listing_by_id(listing_id)
    if listing is None:
        raise _not_found()
    try:
        return service.update_listing(farmer, listing, listing_in)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions") from exc
    except ValueError as exc:
        detail = "quantity_unit must be one of kg, ton, quintal" if str(exc) == "quantity_unit" else "status must be one of available, reserved, sold"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc


@router.delete(
    "/listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a produce listing",
    description="Deletes a listing owned by the authenticated farmer.",
)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> None:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = MarketplaceService(db)
    listing = service.get_listing_by_id(listing_id)
    if listing is None:
        raise _not_found()
    try:
        service.delete_listing(farmer, listing)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions") from exc


@router.get(
    "/my-listings",
    response_model=MarketplaceListingsResponse,
    summary="Get the authenticated farmer's listings",
    description="Returns all listings created by the authenticated farmer.",
)
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer),
) -> MarketplaceListingsResponse:
    farmer = _resolve_farmer_profile(get_farmer_profile(db, current_user.id))
    service = MarketplaceService(db)
    return MarketplaceListingsResponse(items=service.get_my_listings(farmer))