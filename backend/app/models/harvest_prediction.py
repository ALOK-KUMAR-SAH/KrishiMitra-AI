from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class HarvestPredictionHistory(Base):
    __tablename__ = "harvest_prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sowing_date: Mapped[date] = mapped_column(Date, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    farmer = relationship("Farmer", back_populates="harvest_predictions")