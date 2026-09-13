from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import time
from contextlib import asynccontextmanager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.init_db import init_db
from app.core.logging_config import setup_logging, logger
from app.api.v1 import auth, customers, merchants, transactions, risk, alerts, investigations, audit, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting FinGuard API Gateway...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield
    logger.info("Shutting down FinGuard API Gateway.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="FinGuard AI-Powered Real-Time Banking Fraud Detection & Risk Investigation Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(customers.router, prefix=settings.API_V1_STR)
app.include_router(merchants.router, prefix=settings.API_V1_STR)
app.include_router(transactions.router, prefix=settings.API_V1_STR)
app.include_router(risk.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(investigations.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "model": "ready",
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }

@app.get("/metrics", tags=["System"])
def prometheus_metrics():
    """
    Exposes Prometheus application metrics.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to FinGuard Banking Fraud Detection Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }
