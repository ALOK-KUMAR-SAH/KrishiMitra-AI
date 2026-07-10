from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.buyer import Buyer
from app.models.user import User
from app.schemas.buyer import BuyerCreate, BuyerUpdate


def get_buyer_profile(db: Session, user_id: int) -> Buyer | None:
    return db.scalar(select(Buyer).where(Buyer.user_id == user_id))


def create_buyer_profile(db: Session, user: User, buyer_in: BuyerCreate) -> Buyer:
    if get_buyer_profile(db, user.id) is not None:
        raise ValueError("buyer_profile_exists")

    buyer = Buyer(
        user_id=user.id,
        full_name=buyer_in.full_name,
        phone=buyer_in.phone,
        email=buyer_in.email,
        organization_name=buyer_in.organization_name,
        address=buyer_in.address,
        district=buyer_in.district,
        state=buyer_in.state,
        pincode=buyer_in.pincode,
    )
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    return buyer


def update_buyer_profile(db: Session, buyer: Buyer, buyer_in: BuyerUpdate) -> Buyer:
    for field, value in buyer_in.model_dump(exclude_unset=True).items():
        setattr(buyer, field, value)
    db.commit()
    db.refresh(buyer)
    return buyer