from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.logging_config import configure_logging
from app.core.settings import settings

configure_logging()

app = FastAPI(
	title=settings.PROJECT_NAME,
	version=settings.API_VERSION,
	docs_url="/docs",
	redoc_url="/redoc",
	openapi_url="/openapi.json",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.BACKEND_CORS_ORIGINS,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
	return {"message": f"{settings.PROJECT_NAME} is running"}
