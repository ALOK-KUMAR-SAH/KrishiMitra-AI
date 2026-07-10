from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crop_recommendation import CropRecommendationHistory
from app.models.farmer import Farmer
from app.schemas.crop_recommendation import (
    CropPrediction,
    CropRecommendationHistoryItem,
    CropRecommendationRequest,
    CropRecommendationResponse,
)


@dataclass(frozen=True)
class CropProfile:
    name: str
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float


SUPPORTED_CROPS: tuple[CropProfile, ...] = (
    CropProfile("Rice", 90, 40, 40, 27, 80, 6.0, 200),
    CropProfile("Wheat", 85, 35, 35, 22, 55, 6.8, 80),
    CropProfile("Maize", 90, 40, 40, 24, 60, 6.5, 120),
    CropProfile("Cotton", 60, 30, 30, 30, 50, 6.0, 60),
    CropProfile("Sugarcane", 100, 50, 50, 28, 75, 6.5, 250),
    CropProfile("Millet", 40, 20, 20, 30, 40, 7.0, 40),
    CropProfile("Soybean", 60, 45, 45, 26, 65, 6.5, 90),
    CropProfile("Gram", 30, 20, 20, 20, 50, 7.0, 50),
    CropProfile("Mustard", 50, 30, 30, 18, 55, 7.0, 60),
    CropProfile("Groundnut", 40, 30, 30, 28, 60, 6.2, 70),
)


class CropRecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _score_dimension(value: float, ideal: float, tolerance: float) -> float:
        if tolerance <= 0:
            return 0.0
        score = 1 - abs(value - ideal) / tolerance
        return max(0.0, min(score, 1.0))

    def _score_crop(self, request: CropRecommendationRequest, crop: CropProfile) -> float:
        score = 0.0
        score += 15 * self._score_dimension(request.nitrogen, crop.nitrogen, 120)
        score += 10 * self._score_dimension(request.phosphorus, crop.phosphorus, 80)
        score += 10 * self._score_dimension(request.potassium, crop.potassium, 80)
        score += 20 * self._score_dimension(request.temperature, crop.temperature, 18)
        score += 15 * self._score_dimension(request.humidity, crop.humidity, 50)
        score += 10 * self._score_dimension(request.ph, crop.ph, 2)
        score += 20 * self._score_dimension(request.rainfall, crop.rainfall, 250)
        return score

    def predict_top_crops(self, request: CropRecommendationRequest) -> list[CropPrediction]:
        scored_crops = [
            CropPrediction(crop=crop.name, confidence=round(self._score_crop(request, crop) / 100, 4))
            for crop in SUPPORTED_CROPS
        ]
        return sorted(scored_crops, key=lambda item: item.confidence, reverse=True)[:5]

    def save_recommendation(
        self,
        farmer: Farmer,
        request: CropRecommendationRequest,
        recommended_crop: str,
        confidence: float,
    ) -> CropRecommendationHistory:
        history = CropRecommendationHistory(
            farmer_id=farmer.farmer_id,
            nitrogen=request.nitrogen,
            phosphorus=request.phosphorus,
            potassium=request.potassium,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
            recommended_crop=recommended_crop,
            confidence=confidence,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def recommend(self, farmer: Farmer, request: CropRecommendationRequest) -> CropRecommendationResponse:
        top_predictions = self.predict_top_crops(request)
        best_prediction = top_predictions[0]
        history = self.save_recommendation(farmer, request, best_prediction.crop, best_prediction.confidence)
        return CropRecommendationResponse(
            recommended_crop=best_prediction.crop,
            confidence=best_prediction.confidence,
            top_predictions=top_predictions,
            recommendation_id=history.id,
        )

    def get_history(self, farmer: Farmer) -> list[CropRecommendationHistoryItem]:
        statement = (
            select(CropRecommendationHistory)
            .where(CropRecommendationHistory.farmer_id == farmer.farmer_id)
            .order_by(CropRecommendationHistory.created_at.desc(), CropRecommendationHistory.id.desc())
        )
        rows = self.db.scalars(statement).all()
        return [CropRecommendationHistoryItem.model_validate(row) for row in rows]