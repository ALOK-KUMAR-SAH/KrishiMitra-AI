from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CropRecommendationRequest(BaseModel):
    nitrogen: float = Field(ge=0, description="Soil nitrogen level", examples=[90])
    phosphorus: float = Field(ge=0, description="Soil phosphorus level", examples=[42])
    potassium: float = Field(ge=0, description="Soil potassium level", examples=[38])
    temperature: float = Field(ge=-30, le=80, description="Average temperature in Celsius", examples=[26.5])
    humidity: float = Field(ge=0, le=100, description="Relative humidity percentage", examples=[78])
    ph: float = Field(ge=0, le=14, description="Soil pH value", examples=[6.4])
    rainfall: float = Field(ge=0, description="Annual or seasonal rainfall in mm", examples=[180])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nitrogen": 90,
                    "phosphorus": 42,
                    "potassium": 38,
                    "temperature": 26.5,
                    "humidity": 78,
                    "ph": 6.4,
                    "rainfall": 180,
                }
            ]
        }
    )


class CropPrediction(BaseModel):
    crop: str = Field(description="Predicted crop name", examples=["Rice"])
    confidence: float = Field(ge=0, le=1, description="Confidence score from 0 to 1", examples=[0.92])


class CropRecommendationResponse(BaseModel):
    recommended_crop: str = Field(description="Best crop recommendation", examples=["Rice"])
    confidence: float = Field(ge=0, le=1, description="Confidence score from 0 to 1", examples=[0.92])
    top_predictions: list[CropPrediction]
    recommendation_id: int = Field(description="Saved recommendation history id", examples=[101])


class CropRecommendationHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    nitrogen: float
    phosphorus: float
    potassium: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    recommended_crop: str
    confidence: float
    created_at: datetime


CropRecommendationHistoryItem.model_rebuild()