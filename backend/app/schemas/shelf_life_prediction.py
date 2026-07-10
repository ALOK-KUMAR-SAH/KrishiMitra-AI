from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ShelfLifePredictionRequest(BaseModel):
    crop_name: str = Field(description="Crop name", examples=["Tomato"])
    harvest_date: date = Field(description="Harvest date in ISO format", examples=["2026-07-01"])
    storage_type: str = Field(description="Storage method used after harvest", examples=["Cold Storage"])
    temperature: float = Field(ge=-10, le=60, description="Storage temperature in Celsius", examples=["4.5"])
    humidity: float = Field(ge=0, le=100, description="Storage relative humidity percentage", examples=["78"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "crop_name": "Tomato",
                    "harvest_date": "2026-07-01",
                    "storage_type": "Cold Storage",
                    "temperature": 4.5,
                    "humidity": 78,
                }
            ]
        }
    )

    @model_validator(mode="after")
    def validate_harvest_date(self) -> "ShelfLifePredictionRequest":
        if self.harvest_date > date.today():
            raise ValueError("harvest_date must not be in the future")
        return self


class ShelfLifePredictionResponse(BaseModel):
    crop_name: str = Field(description="Crop name used for prediction")
    harvest_date: date = Field(description="Harvest date used for prediction")
    storage_type: str = Field(description="Storage type used for prediction")
    temperature: float = Field(description="Storage temperature in Celsius")
    humidity: float = Field(description="Storage relative humidity percentage")
    predicted_shelf_life_days: int = Field(description="Estimated shelf life in days", examples=[14])
    remaining_days: int = Field(description="Estimated remaining freshness in days", examples=[7])
    freshness_score: float = Field(ge=0, le=100, description="Freshness score from 0 to 100", examples=[74.5])
    recommendation: str = Field(description="Recommended storage or handling action")
    recommendation_id: int = Field(description="Saved shelf-life prediction history id", examples=[401])


class ShelfLifePredictionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    crop_name: str
    harvest_date: date
    storage_type: str
    temperature: float
    humidity: float
    predicted_shelf_life_days: int
    remaining_days: int
    freshness_score: float
    recommendation: str
    created_at: datetime


class ShelfLifePredictionHistoryResponse(BaseModel):
    items: list[ShelfLifePredictionHistoryItem]