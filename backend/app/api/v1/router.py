from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.disease import router as disease_router
from app.api.v1.endpoints.crop import router as crop_router
from app.api.v1.endpoints.harvest import router as harvest_router
from app.api.v1.endpoints.shelf_life import router as shelf_life_router
from app.api.v1.endpoints.quality import router as quality_router
from app.api.v1.endpoints.marketplace import router as marketplace_router
from app.api.v1.endpoints.farmers import router as farmers_router
from app.api.v1.endpoints.health import router as health_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(disease_router)
router.include_router(crop_router)
router.include_router(harvest_router)
router.include_router(shelf_life_router)
router.include_router(quality_router)
router.include_router(marketplace_router)
router.include_router(farmers_router)
router.include_router(health_router)
