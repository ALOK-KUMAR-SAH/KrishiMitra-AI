from fastapi import APIRouter

from app.core.settings import settings
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        database="not configured",
    )