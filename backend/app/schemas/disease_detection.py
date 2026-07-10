from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field


DiseaseDetectionRequest = Annotated[
    UploadFile,
    File(description="Upload a JPG, JPEG, or PNG crop image up to 10 MB."),
]


class DiseasePrediction(BaseModel):
    disease: str = Field(description="Predicted disease or healthy status", examples=["Leaf Blast"])
    confidence: float = Field(ge=0, le=1, description="Confidence score from 0 to 1", examples=[0.94])


class DiseaseDetectionResponse(BaseModel):
    crop_name: str = Field(description="Detected crop name", examples=["Rice"])
    predicted_disease: str = Field(description="Most likely disease or healthy status", examples=["Leaf Blast"])
    confidence: float = Field(ge=0, le=1, description="Confidence score from 0 to 1", examples=[0.94])
    recommended_solution: str = Field(description="Suggested treatment or next action")
    recommendation_id: int = Field(description="Saved detection history id", examples=[201])


class DiseaseDetectionHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    image_path: str
    crop_name: str
    predicted_disease: str
    confidence: float
    recommended_solution: str
    created_at: datetime