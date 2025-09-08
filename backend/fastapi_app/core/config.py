"""
Configuration settings for Incognito Technology FastAPI application
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Incognito Technology API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Security
    SECRET_KEY: str = Field(..., env="JWT_SECRET")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    MONGODB_URL: str = Field(..., env="MONGODB_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # External Services
    BLOCKCHAIN_URL: str = Field(default="http://localhost:8545", env="BLOCKCHAIN_URL")
    AI_MODEL_PATH: str = Field(default="/app/models", env="MODEL_PATH")
    
    # Encryption
    ENCRYPTION_KEY: str = Field(..., env="ENCRYPTION_KEY")
    
    # Monitoring
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
