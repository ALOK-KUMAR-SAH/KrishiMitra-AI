from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MarketplaceListingBase(BaseModel):
    crop_name: str = Field(min_length=1, max_length=100, description="Crop name", examples=["Tomato"])
    quantity: float = Field(gt=0, description="Quantity of produce", examples=[120.5])
    quantity_unit: str = Field(description="Unit of quantity", examples=["kg"])
    expected_price: float = Field(gt=0, description="Expected asking price", examples=[2400.0])
    quality_grade: str = Field(min_length=1, max_length=1, description="Quality grade", examples=["A"])
    district: str = Field(min_length=1, max_length=100, description="District", examples=["Pune"])
    state: str = Field(min_length=1, max_length=100, description="State", examples=["Maharashtra"])
    description: str = Field(min_length=1, max_length=2000, description="Listing description", examples=["Fresh produce from organic farm."])
    harvest_date: date = Field(description="Harvest date", examples=["2026-06-20"])
    status: str = Field(default="available", description="Listing status", examples=["available"])
    image_path: str | None = Field(default=None, description="Optional relative image path", examples=["uploads/marketplace/tomato.jpg"])


class MarketplaceListingCreate(MarketplaceListingBase):
    pass


class MarketplaceListingUpdate(BaseModel):
    crop_name: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: float | None = Field(default=None, gt=0)
    quantity_unit: str | None = None
    expected_price: float | None = Field(default=None, gt=0)
    quality_grade: str | None = Field(default=None, min_length=1, max_length=1)
    district: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    harvest_date: date | None = None
    status: str | None = None
    image_path: str | None = None


class MarketplaceListingResponse(MarketplaceListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    created_at: datetime
    updated_at: datetime


class MarketplaceListingsResponse(BaseModel):
    items: list[MarketplaceListingResponse]