from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    farmer = "farmer"
    buyer = "buyer"
    consumer = "consumer"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.farmer


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


UserRead = UserResponse
