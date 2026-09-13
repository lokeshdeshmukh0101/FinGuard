from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinGuard Fraud Detection API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./finguard.db"

    # Security
    SECRET_KEY: str = "finguard-super-secret-development-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Risk Engine Weights
    RULE_WEIGHT: float = 0.4
    ML_WEIGHT: float = 0.6
    MODEL_PATH: str = "../ml/models/fraud_detector_v1.joblib"

    # Risk Thresholds
    RISK_THRESHOLD_MEDIUM: float = 40.0
    RISK_THRESHOLD_HIGH: float = 70.0

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
