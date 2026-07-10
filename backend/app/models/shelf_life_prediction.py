from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ShelfLifePredictionHistory(Base):
    __tablename__ = "shelf_life_prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    storage_type: Mapped[str] = mapped_column(String(100), nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    humidity: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    predicted_shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_days: Mapped[int] = mapped_column(Integer, nullable=False)
    freshness_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    farmer = relationship("Farmer", back_populates="shelf_life_predictions")