from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.shelf_life_prediction import ShelfLifePredictionHistory
from app.schemas.shelf_life_prediction import (
    ShelfLifePredictionHistoryItem,
    ShelfLifePredictionRequest,
    ShelfLifePredictionResponse,
)


@dataclass(frozen=True)
class ShelfLifeProfile:
    crop_name: str
    base_days: int
    storage_bonus: int
    storage_loss: int


SUPPORTED_CROPS: tuple[str, ...] = ("Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato")
STORAGE_PROFILES: dict[str, ShelfLifeProfile] = {
    "cold storage": ShelfLifeProfile("cold storage", 0, 4, 0),
    "refrigerated": ShelfLifeProfile("refrigerated", 0, 3, 0),
    "room temperature": ShelfLifeProfile("room temperature", 0, 0, 0),
    "ambient": ShelfLifeProfile("ambient", 0, 0, 1),
    "ventilated": ShelfLifeProfile("ventilated", 0, 1, 0),
}

BASE_SHELF_LIFE_DAYS: dict[str, int] = {
    "Rice": 30,
    "Wheat": 45,
    "Maize": 10,
    "Cotton": 20,
    "Tomato": 12,
    "Potato": 25,
}


class ShelfLifePredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _normalize_crop_name(crop_name: str) -> str:
        return crop_name.strip().title()

    @staticmethod
    def _normalize_storage_type(storage_type: str) -> str:
        return storage_type.strip().lower()

    def _base_shelf_life(self, crop_name: str) -> int:
        normalized = self._normalize_crop_name(crop_name)
        return BASE_SHELF_LIFE_DAYS.get(normalized, 18)

    @staticmethod
    def _temperature_adjustment(temperature: float, storage_type: str) -> int:
        normalized_storage = storage_type.strip().lower()
        if normalized_storage in {"cold storage", "refrigerated"}:
            if temperature <= 5:
                return 5
            if temperature <= 8:
                return 2
            return -3
        if temperature <= 15:
            return 1
        if temperature <= 25:
            return 0
        if temperature <= 35:
            return -2
        return -5

    @staticmethod
    def _humidity_adjustment(humidity: float) -> int:
        if humidity < 40:
            return -2
        if humidity <= 70:
            return 1
        if humidity <= 85:
            return 0
        return -3

    @staticmethod
    def _storage_adjustment(storage_type: str) -> int:
        normalized = storage_type.strip().lower()
        if normalized in {"cold storage", "refrigerated"}:
            return 5
        if normalized in {"ventilated", "room temperature"}:
            return 1
        if normalized == "ambient":
            return -1
        return 0

    def predict_shelf_life(self, request: ShelfLifePredictionRequest) -> tuple[int, int, float, str]:
        crop_name = self._normalize_crop_name(request.crop_name)
        storage_type = request.storage_type.strip()
        base_days = self._base_shelf_life(crop_name)
        temperature_adjustment = self._temperature_adjustment(request.temperature, storage_type)
        humidity_adjustment = self._humidity_adjustment(request.humidity)
        storage_adjustment = self._storage_adjustment(storage_type)
        predicted_shelf_life_days = max(1, base_days + temperature_adjustment + humidity_adjustment + storage_adjustment)
        days_elapsed = max(0, (date.today() - request.harvest_date).days)
        remaining_days = max(0, predicted_shelf_life_days - days_elapsed)
        freshness_score = round(max(0.0, min(100.0, (remaining_days / predicted_shelf_life_days) * 100)), 2)

        if remaining_days == 0:
            recommendation = "Consume or process immediately; the shelf life window has likely been exhausted."
        elif storage_type.strip().lower() in {"cold storage", "refrigerated"}:
            recommendation = "Maintain consistent cold storage, avoid repeated temperature changes, and inspect for moisture buildup."
        elif request.temperature > 25:
            recommendation = "Move to a cooler storage environment and reduce exposure to heat and direct sunlight."
        elif request.humidity > 80:
            recommendation = "Reduce humidity, improve ventilation, and remove any damaged produce to slow spoilage."
        else:
            recommendation = "Store in a clean, dry, ventilated space and inspect regularly for quality loss."

        return predicted_shelf_life_days, remaining_days, freshness_score, recommendation

    def save_prediction(
        self,
        farmer: Farmer,
        request: ShelfLifePredictionRequest,
        predicted_shelf_life_days: int,
        remaining_days: int,
        freshness_score: float,
        recommendation: str,
    ) -> ShelfLifePredictionHistory:
        history = ShelfLifePredictionHistory(
            farmer_id=farmer.farmer_id,
            crop_name=self._normalize_crop_name(request.crop_name),
            harvest_date=request.harvest_date,
            storage_type=request.storage_type.strip(),
            temperature=request.temperature,
            humidity=request.humidity,
            predicted_shelf_life_days=predicted_shelf_life_days,
            remaining_days=remaining_days,
            freshness_score=freshness_score,
            recommendation=recommendation,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def predict(self, farmer: Farmer, request: ShelfLifePredictionRequest) -> ShelfLifePredictionResponse:
        predicted_shelf_life_days, remaining_days, freshness_score, recommendation = self.predict_shelf_life(request)
        history = self.save_prediction(
            farmer,
            request,
            predicted_shelf_life_days,
            remaining_days,
            freshness_score,
            recommendation,
        )
        return ShelfLifePredictionResponse(
            crop_name=self._normalize_crop_name(request.crop_name),
            harvest_date=request.harvest_date,
            storage_type=request.storage_type.strip(),
            temperature=request.temperature,
            humidity=request.humidity,
            predicted_shelf_life_days=predicted_shelf_life_days,
            remaining_days=remaining_days,
            freshness_score=freshness_score,
            recommendation=recommendation,
            recommendation_id=history.id,
        )

    def get_history(self, farmer: Farmer) -> list[ShelfLifePredictionHistoryItem]:
        statement = (
            select(ShelfLifePredictionHistory)
            .where(ShelfLifePredictionHistory.farmer_id == farmer.farmer_id)
            .order_by(ShelfLifePredictionHistory.created_at.desc(), ShelfLifePredictionHistory.id.desc())
        )
        rows = self.db.scalars(statement).all()
        return [ShelfLifePredictionHistoryItem.model_validate(row) for row in rows]