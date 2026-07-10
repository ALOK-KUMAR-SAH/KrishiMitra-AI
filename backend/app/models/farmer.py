from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    farmer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    aadhaar: Mapped[str | None] = mapped_column(String(12), unique=True, nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    village: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    farm_size: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    soil_type: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_crop: Mapped[str] = mapped_column(String(100), nullable=False)
    secondary_crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="farmer_profile")
    recommendations = relationship("CropRecommendationHistory", back_populates="farmer", cascade="all, delete-orphan")
    disease_detections = relationship("DiseaseDetectionHistory", back_populates="farmer", cascade="all, delete-orphan")
    harvest_predictions = relationship("HarvestPredictionHistory", back_populates="farmer", cascade="all, delete-orphan")
    shelf_life_predictions = relationship("ShelfLifePredictionHistory", back_populates="farmer", cascade="all, delete-orphan")