from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.marketplace import MarketplaceListing
from app.schemas.marketplace import MarketplaceListingCreate, MarketplaceListingUpdate


ALLOWED_QUANTITY_UNITS: tuple[str, ...] = ("kg", "ton", "quintal")
ALLOWED_STATUSES: tuple[str, ...] = ("available", "reserved", "sold")


class MarketplaceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _normalize_quantity_unit(quantity_unit: str) -> str:
        return quantity_unit.strip().lower()

    @staticmethod
    def _normalize_status(status: str) -> str:
        return status.strip().lower()

    def _validate_listing(self, listing_in: MarketplaceListingCreate | MarketplaceListingUpdate) -> None:
        if listing_in.quantity_unit is not None and self._normalize_quantity_unit(listing_in.quantity_unit) not in ALLOWED_QUANTITY_UNITS:
            raise ValueError("quantity_unit")
        if listing_in.status is not None and self._normalize_status(listing_in.status) not in ALLOWED_STATUSES:
            raise ValueError("status")

    def create_listing(self, farmer: Farmer, listing_in: MarketplaceListingCreate) -> MarketplaceListing:
        self._validate_listing(listing_in)
        listing = MarketplaceListing(
            farmer_id=farmer.farmer_id,
            crop_name=listing_in.crop_name.strip().title(),
            quantity=listing_in.quantity,
            quantity_unit=self._normalize_quantity_unit(listing_in.quantity_unit),
            expected_price=listing_in.expected_price,
            quality_grade=listing_in.quality_grade.strip().upper(),
            district=listing_in.district.strip(),
            state=listing_in.state.strip(),
            description=listing_in.description.strip(),
            harvest_date=listing_in.harvest_date,
            status=self._normalize_status(listing_in.status),
            image_path=listing_in.image_path,
        )
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def get_public_listings(self) -> list[MarketplaceListing]:
        statement = (
            select(MarketplaceListing)
            .where(MarketplaceListing.status == "available")
            .order_by(MarketplaceListing.created_at.desc(), MarketplaceListing.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_listing_by_id(self, listing_id: int) -> MarketplaceListing | None:
        statement = select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
        return self.db.scalar(statement)

    def get_listing_for_view(self, listing_id: int, farmer: Farmer | None = None) -> MarketplaceListing | None:
        listing = self.get_listing_by_id(listing_id)
        if listing is None:
            return None
        if listing.status == "available":
            return listing
        if farmer is not None and listing.farmer_id == farmer.farmer_id:
            return listing
        return None

    def get_my_listings(self, farmer: Farmer) -> list[MarketplaceListing]:
        statement = (
            select(MarketplaceListing)
            .where(MarketplaceListing.farmer_id == farmer.farmer_id)
            .order_by(MarketplaceListing.created_at.desc(), MarketplaceListing.id.desc())
        )
        return list(self.db.scalars(statement).all())

    def update_listing(self, farmer: Farmer, listing: MarketplaceListing, listing_in: MarketplaceListingUpdate) -> MarketplaceListing:
        if listing.farmer_id != farmer.farmer_id:
            raise PermissionError("forbidden")
        self._validate_listing(listing_in)
        update_data = listing_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "crop_name" and value is not None:
                value = value.strip().title()
            elif field == "quantity_unit" and value is not None:
                value = self._normalize_quantity_unit(value)
            elif field == "quality_grade" and value is not None:
                value = value.strip().upper()
            elif field in {"district", "state", "description", "status", "image_path"} and value is not None:
                value = value.strip() if isinstance(value, str) else value
                if field == "status" and value is not None:
                    value = self._normalize_status(value)
            setattr(listing, field, value)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def delete_listing(self, farmer: Farmer, listing: MarketplaceListing) -> None:
        if listing.farmer_id != farmer.farmer_id:
            raise PermissionError("forbidden")
        self.db.delete(listing)
        self.db.commit()