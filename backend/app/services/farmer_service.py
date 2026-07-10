from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.user import User
from app.schemas.farmer import FarmerCreate, FarmerUpdate


def get_farmer_profile(db: Session, user_id: int) -> Farmer | None:
    return db.scalar(select(Farmer).where(Farmer.user_id == user_id))


def create_farmer_profile(db: Session, user: User, farmer_in: FarmerCreate) -> Farmer:
    farmer = Farmer(user_id=user.id, **farmer_in.model_dump())
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


def update_farmer_profile(db: Session, farmer: Farmer, farmer_in: FarmerUpdate) -> Farmer:
    for field, value in farmer_in.model_dump().items():
        setattr(farmer, field, value)
    db.commit()
    db.refresh(farmer)
    return farmer