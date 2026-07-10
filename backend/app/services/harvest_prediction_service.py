from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.harvest_prediction import HarvestPredictionHistory
from app.schemas.harvest_prediction import (
    HarvestPredictionHistoryItem,
    HarvestPredictionRequest,
    HarvestPredictionResponse,
)


@dataclass(frozen=True)
class HarvestProfile:
    crop_name: str
    base_days_to_harvest: int
    confidence_floor: float


SUPPORTED_HARVEST_PROFILES: tuple[HarvestProfile, ...] = (
    HarvestProfile("Rice", 120, 0.86),
    HarvestProfile("Wheat", 135, 0.88),
    HarvestProfile("Maize", 100, 0.87),
    HarvestProfile("Cotton", 170, 0.84),
    HarvestProfile("Sugarcane", 300, 0.81),
    HarvestProfile("Millet", 80, 0.85),
    HarvestProfile("Soybean", 95, 0.86),
    HarvestProfile("Gram", 105, 0.83),
    HarvestProfile("Mustard", 125, 0.84),
    HarvestProfile("Groundnut", 140, 0.82),
)


class HarvestPredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _normalize_crop_name(crop_name: str) -> str:
        return crop_name.strip().title()

    def _get_profile(self, crop_name: str) -> HarvestProfile:
        normalized = self._normalize_crop_name(crop_name)
        for profile in SUPPORTED_HARVEST_PROFILES:
            if profile.crop_name == normalized:
                return profile
        return HarvestProfile(normalized, 110, 0.80)

    @staticmethod
    def _location_adjustment(district: str, state: str) -> int:
        seed = sum(ord(character) for character in f"{district.lower()}::{state.lower()}")
        return (seed % 11) - 5

    @staticmethod
    def _seasonal_adjustment(sowing_date: date, crop_name: str) -> int:
        month = sowing_date.month
        crop_factor = len(crop_name) % 4
        if month in {6, 7, 8, 9}:
            return -3 + crop_factor
        if month in {10, 11, 12}:
            return 2 + crop_factor
        return crop_factor

    def predict_harvest(self, request: HarvestPredictionRequest) -> tuple[date, int, float]:
        profile = self._get_profile(request.crop_name)
        location_adjustment = self._location_adjustment(request.district, request.state)
        seasonal_adjustment = self._seasonal_adjustment(request.sowing_date, profile.crop_name)
        total_days = max(15, profile.base_days_to_harvest + location_adjustment + seasonal_adjustment)
        predicted_harvest_date = request.sowing_date + timedelta(days=total_days)
        days_remaining = max(0, (predicted_harvest_date - date.today()).days)
        confidence = min(0.98, profile.confidence_floor + (abs(location_adjustment) * 0.01) + (abs(seasonal_adjustment) * 0.005))
        return predicted_harvest_date, days_remaining, round(confidence, 4)

    def save_prediction(
        self,
        farmer: Farmer,
        request: HarvestPredictionRequest,
        predicted_harvest_date: date,
        days_remaining: int,
        confidence: float,
    ) -> HarvestPredictionHistory:
        history = HarvestPredictionHistory(
            farmer_id=farmer.farmer_id,
            crop_name=self._normalize_crop_name(request.crop_name),
            sowing_date=request.sowing_date,
            district=request.district,
            state=request.state,
            predicted_harvest_date=predicted_harvest_date,
            days_remaining=days_remaining,
            confidence=confidence,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def predict(self, farmer: Farmer, request: HarvestPredictionRequest) -> HarvestPredictionResponse:
        predicted_harvest_date, days_remaining, confidence = self.predict_harvest(request)
        history = self.save_prediction(farmer, request, predicted_harvest_date, days_remaining, confidence)
        return HarvestPredictionResponse(
            crop_name=self._normalize_crop_name(request.crop_name),
            sowing_date=request.sowing_date,
            district=request.district,
            state=request.state,
            predicted_harvest_date=predicted_harvest_date,
            days_remaining=days_remaining,
            confidence=confidence,
            recommendation_id=history.id,
        )

    def get_history(self, farmer: Farmer) -> list[HarvestPredictionHistoryItem]:
        statement = (
            select(HarvestPredictionHistory)
            .where(HarvestPredictionHistory.farmer_id == farmer.farmer_id)
            .order_by(HarvestPredictionHistory.created_at.desc(), HarvestPredictionHistory.id.desc())
        )
        rows = self.db.scalars(statement).all()
        return [HarvestPredictionHistoryItem.model_validate(row) for row in rows]