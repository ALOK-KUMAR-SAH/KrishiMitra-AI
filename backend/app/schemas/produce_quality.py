from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field


QualityGradingRequest = Annotated[
    UploadFile,
    File(description="Upload a JPG, JPEG, or PNG image up to 10 MB for quality grading."),
]


class QualityPrediction(BaseModel):
    grade: str = Field(description="Quality grade", examples=["A"])
    quality_score: float = Field(ge=0, le=100, description="Quality score from 0 to 100", examples=[92.5])


class QualityGradingResponse(BaseModel):
    crop_name: str = Field(description="Crop name provided for grading", examples=["Tomato"])
    grade: str = Field(description="Predicted grade", examples=["A"])
    quality_score: float = Field(ge=0, le=100, description="Quality score from 0 to 100", examples=[92.5])
    defects: list[str] = Field(description="Detected defects", examples=[["Minor bruising"]])
    recommendation: str = Field(description="Quality handling recommendation")
    recommendation_id: int = Field(description="Saved quality history id", examples=[501])


class QualityHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    farmer_id: int
    crop_name: str
    image_path: str
    grade: str
    quality_score: float
    defects: str
    recommendation: str
    created_at: datetime


class QualityHistoryResponse(BaseModel):
    items: list[QualityHistoryItem]