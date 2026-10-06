from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401
from app.api.routes.analytics import router as analytics_router
from app.api.routes.anomaly import router as anomaly_router
from app.api.routes.auth import router as auth_router
from app.api.routes.network import router as network_router
from app.api.routes.prediction import router as prediction_router
from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.database.connection import create_db_and_tables

settings = get_settings()
logger = setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    logger.info("Database tables created or validated")
    yield


app = FastAPI(
    title="Telecom Network Intelligence Platform",
    description="ML-based telecom network quality prediction and anomaly detection API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.include_router(auth_router)
app.include_router(network_router)
app.include_router(prediction_router)
app.include_router(anomaly_router)
app.include_router(analytics_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/ui")
async def ui() -> FileResponse:
    return FileResponse("app/static/index.html")


@app.get("/")
async def root() -> dict[str, str]:
    logger.info("Root endpoint called")
    return {"message": "Telecom Network Intelligence Platform is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": settings.app_name}


@app.get("/healthz")
async def readiness() -> dict[str, str]:
    return {"status": "ready", "service": settings.app_name}
