from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.disease_detection import DiseaseDetectionHistory
from app.models.farmer import Farmer
from app.schemas.disease_detection import (
    DiseaseDetectionHistoryItem,
    DiseaseDetectionResponse,
)


SUPPORTED_CROPS: tuple[str, ...] = ("Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato")
SUPPORTED_DISEASES: tuple[str, ...] = ("Leaf Blast", "Leaf Spot", "Rust", "Powdery Mildew", "Bacterial Blight", "Healthy")
ALLOWED_CONTENT_TYPES: tuple[str, ...] = ("image/jpeg", "image/png")
ALLOWED_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class DiseasePredictionResult:
    crop_name: str
    predicted_disease: str
    confidence: float
    recommended_solution: str


class DiseaseDetectionService:
    def __init__(self, db: Session, upload_dir: Path | None = None) -> None:
        self.db = db
        self.upload_dir = upload_dir or Path(__file__).resolve().parents[2] / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

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
        relative_path = Path("uploads") / filename
        destination = self.upload_dir / filename
        destination.write_bytes(file_bytes)
        await image.close()
        return relative_path.as_posix()

    @staticmethod
    def _mock_predict(image_path: str) -> DiseasePredictionResult:
        # Replace this method with a trained vision model later.
        score = sum(ord(character) for character in image_path)
        crop_name = SUPPORTED_CROPS[score % len(SUPPORTED_CROPS)]
        disease_index = (score // 7) % len(SUPPORTED_DISEASES)
        predicted_disease = SUPPORTED_DISEASES[disease_index]
        if crop_name in {"Rice", "Wheat", "Maize"} and predicted_disease == "Healthy":
            predicted_disease = SUPPORTED_DISEASES[(disease_index + 1) % len(SUPPORTED_DISEASES)]

        confidence = round(0.78 + (score % 17) / 100, 4)
        if predicted_disease == "Healthy":
            solution = "No treatment required. Continue monitoring the crop and maintain standard field hygiene."
        elif predicted_disease in {"Leaf Blast", "Rust"}:
            solution = "Remove affected leaves, reduce humidity around plants, and apply a recommended fungicide as per local agronomist guidance."
        elif predicted_disease == "Leaf Spot":
            solution = "Prune infected foliage, improve spacing for airflow, and use a suitable preventive spray if advised locally."
        elif predicted_disease == "Powdery Mildew":
            solution = "Improve field ventilation, avoid excess nitrogen, and treat with an approved fungicide when necessary."
        else:
            solution = "Isolate infected plants, sanitize tools, and follow crop-specific disease management guidance from a qualified agronomist."

        return DiseasePredictionResult(
            crop_name=crop_name,
            predicted_disease=predicted_disease,
            confidence=confidence,
            recommended_solution=solution,
        )

    def save_detection(
        self,
        farmer: Farmer,
        image_path: str,
        prediction: DiseasePredictionResult,
    ) -> DiseaseDetectionHistory:
        detection = DiseaseDetectionHistory(
            farmer_id=farmer.farmer_id,
            image_path=image_path,
            crop_name=prediction.crop_name,
            predicted_disease=prediction.predicted_disease,
            confidence=prediction.confidence,
            recommended_solution=prediction.recommended_solution,
        )
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        return detection

    async def predict(self, farmer: Farmer, image: UploadFile) -> DiseaseDetectionResponse:
        image_path = await self.save_image(image)
        prediction = self._mock_predict(image_path)
        history = self.save_detection(farmer, image_path, prediction)
        return DiseaseDetectionResponse(
            crop_name=prediction.crop_name,
            predicted_disease=prediction.predicted_disease,
            confidence=prediction.confidence,
            recommended_solution=prediction.recommended_solution,
            recommendation_id=history.id,
        )

    def get_history(self, farmer: Farmer) -> list[DiseaseDetectionHistoryItem]:
        statement = (
            select(DiseaseDetectionHistory)
            .where(DiseaseDetectionHistory.farmer_id == farmer.farmer_id)
            .order_by(DiseaseDetectionHistory.created_at.desc(), DiseaseDetectionHistory.id.desc())
        )
        rows = self.db.scalars(statement).all()
        return [DiseaseDetectionHistoryItem.model_validate(row) for row in rows]