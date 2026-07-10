from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.produce_quality import ProduceQualityHistory
from app.schemas.produce_quality import QualityGradingResponse, QualityHistoryItem


SUPPORTED_CROPS: tuple[str, ...] = ("Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato")
ALLOWED_CONTENT_TYPES: tuple[str, ...] = ("image/jpeg", "image/png")
ALLOWED_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class QualityPredictionResult:
    grade: str
    quality_score: float
    defects: list[str]
    recommendation: str


class ProduceQualityService:
    def __init__(self, db: Session, upload_dir: Path | None = None) -> None:
        self.db = db
        self.upload_dir = upload_dir or Path(__file__).resolve().parents[2] / "uploads" / "quality"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalize_crop_name(crop_name: str) -> str:
        return crop_name.strip().title()

    def _validate_upload(self, image: UploadFile) -> str:
        filename = image.filename or ""
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only jpg, jpeg, and png images are allowed",
            )
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only jpg, jpeg, and png images are allowed",
            )
        return extension

    async def save_image(self, image: UploadFile) -> str:
        extension = self._validate_upload(image)
        image.file.seek(0)
        file_bytes = await image.read()
        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image size must be 10 MB or less",
            )
        is_jpeg = file_bytes.startswith(JPEG_MAGIC)
        is_png = file_bytes.startswith(PNG_MAGIC)
        if not (is_jpeg or is_png):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is not a valid image",
            )

        filename = f"{uuid4().hex}{extension}"
        relative_path = Path("uploads") / "quality" / filename
        destination = self.upload_dir / filename
        destination.write_bytes(file_bytes)
        await image.close()
        return relative_path.as_posix()

    def _mock_grade(self, crop_name: str, image_path: str) -> QualityPredictionResult:
        seed = sum(ord(character) for character in f"{crop_name.lower()}::{image_path.lower()}")
        normalized_crop = self._normalize_crop_name(crop_name)
        if normalized_crop not in SUPPORTED_CROPS:
            normalized_crop = SUPPORTED_CROPS[seed % len(SUPPORTED_CROPS)]

        score = 55 + (seed % 41)
        if score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        else:
            grade = "C"

        defects: list[str] = []
        if grade == "A":
            defects = ["No significant visible defects"]
        elif grade == "B":
            defects = ["Minor bruising", "Slight color variation"]
        else:
            defects = ["Visible blemishes", "Shape irregularities", "Surface damage"]

        if normalized_crop in {"Tomato", "Potato"} and grade == "C":
            recommendation = "Sort carefully, remove damaged produce, and prioritize immediate sale or processing."
        elif grade == "A":
            recommendation = "Pack in clean containers and maintain cool storage to preserve premium quality."
        elif grade == "B":
            recommendation = "Grade separately, handle gently, and store in a cool dry place for better shelf retention."
        else:
            recommendation = "Use for processing or local markets first, and isolate damaged produce to reduce spoilage."

        quality_score = round(float(score), 2)
        return QualityPredictionResult(
            grade=grade,
            quality_score=quality_score,
            defects=defects,
            recommendation=recommendation,
        )

    def save_prediction(
        self,
        farmer: Farmer,
        crop_name: str,
        image_path: str,
        prediction: QualityPredictionResult,
    ) -> ProduceQualityHistory:
        history = ProduceQualityHistory(
            farmer_id=farmer.farmer_id,
            crop_name=self._normalize_crop_name(crop_name),
            image_path=image_path,
            grade=prediction.grade,
            quality_score=prediction.quality_score,
            defects=", ".join(prediction.defects),
            recommendation=prediction.recommendation,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    async def grade(self, farmer: Farmer, crop_name: str, image: UploadFile) -> QualityGradingResponse:
        image_path = await self.save_image(image)
        prediction = self._mock_grade(crop_name, image_path)
        history = self.save_prediction(farmer, crop_name, image_path, prediction)
        return QualityGradingResponse(
            crop_name=self._normalize_crop_name(crop_name),
            grade=prediction.grade,
            quality_score=prediction.quality_score,
            defects=prediction.defects,
            recommendation=prediction.recommendation,
            recommendation_id=history.id,
        )

    def get_history(self, farmer: Farmer) -> list[QualityHistoryItem]:
        statement = (
            select(ProduceQualityHistory)
            .where(ProduceQualityHistory.farmer_id == farmer.farmer_id)
            .order_by(ProduceQualityHistory.created_at.desc(), ProduceQualityHistory.id.desc())
        )
        rows = self.db.scalars(statement).all()
        return [QualityHistoryItem.model_validate(row) for row in rows]