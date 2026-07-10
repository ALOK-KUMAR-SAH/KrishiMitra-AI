from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class CropRecommendationHistory(Base):
    __tablename__ = "crop_recommendation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.farmer_id", ondelete="CASCADE"), nullable=False, index=True)
    nitrogen: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    phosphorus: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    potassium: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    humidity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    ph: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    rainfall: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    recommended_crop: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    farmer = relationship("Farmer", back_populates="recommendations")