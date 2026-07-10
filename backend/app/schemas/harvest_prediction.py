from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class HarvestPredictionRequest(BaseModel):
    crop_name: str = Field(description="Name of the sown crop", examples=["Rice"])
    sowing_date: date = Field(description="Sowing date in ISO format", examples=["2026-05-15"])
    district: str = Field(min_length=1, max_length=100, description="District where the crop was sown", examples=["Nagpur"])
    state: str = Field(min_length=1, max_length=100, description="State where the crop was sown", examples=["Maharashtra"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "crop_name": "Rice",
                    "sowing_date": "2026-05-15",
                    "district": "Nagpur",
                    "state": "Maharashtra",
                }
            ]
        }
    )


class HarvestPredictionResponse(BaseModel):
    crop_name: str = Field(description="Crop name used for prediction", examples=["Rice"])
    sowing_date: date = Field(description="Sowing date used for prediction")
    district: str = Field(description="District used for prediction")
    state: str = Field(description="State used for prediction")
    predicted_harvest_date: date = Field(description="Estimated harvest date")
    days_remaining: int = Field(description="Estimated days remaining until harvest", examples=[45])
    confidence: float = Field(ge=0, le=1, description="Prediction confidence score", examples=[0.89])
    recommendation_id: int = Field(description="Saved prediction history id", examples=[301])


class HarvestPredictionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    crop_name: str
    sowing_date: date
    district: str
    state: str
    predicted_harvest_date: date
    days_remaining: int
    confidence: float
    created_at: datetime


class HarvestPredictionHistoryResponse(BaseModel):
    items: list[HarvestPredictionHistoryItem]