from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BuyerBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=7, max_length=20)
    email: EmailStr
    organization_name: str | None = Field(default=None, max_length=255)
    address: str = Field(min_length=1, max_length=255)
    district: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    pincode: str = Field(min_length=4, max_length=10)


class BuyerCreate(BuyerBase):
    pass


class BuyerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    email: EmailStr | None = None
    organization_name: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    district: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    pincode: str | None = Field(default=None, min_length=4, max_length=10)


class BuyerResponse(BuyerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime