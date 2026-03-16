from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    app_name: str = "CareerShield AI"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./careershield.db"
    anthropic_api_key: str = ""
    bls_api_key: str = ""
    cors_origins: str = "http://localhost:5173"
    ml_models_path: str = "./backend/ml/saved_models"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
