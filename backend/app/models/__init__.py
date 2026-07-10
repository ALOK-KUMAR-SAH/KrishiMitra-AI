from app.models.user import User
from app.models.farmer import Farmer
from app.models.crop_recommendation import CropRecommendationHistory
from app.models.disease_detection import DiseaseDetectionHistory

__all__ = ["CropRecommendationHistory", "DiseaseDetectionHistory", "Farmer", "User"]
