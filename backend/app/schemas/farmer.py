from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class FarmerBase(BaseModel):
    aadhaar: str | None = Field(default=None, min_length=12, max_length=12)
    state: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    village: str = Field(min_length=1, max_length=100)
    pincode: str = Field(min_length=4, max_length=10)
    farm_size: Decimal = Field(gt=0)
    soil_type: str = Field(min_length=1, max_length=100)
    primary_crop: str = Field(min_length=1, max_length=100)
    secondary_crop: str | None = Field(default=None, max_length=100)
    experience_years: int = Field(ge=0)
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(FarmerBase):
    pass


class FarmerResponse(FarmerBase):
    model_config = ConfigDict(from_attributes=True)

    farmer_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime