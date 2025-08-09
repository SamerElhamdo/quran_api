import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class BaseConfig:
    """Base configuration class."""
    
    # Flask
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///quran_dev.db"
    SQLITE_DATABASE_URL: str = "sqlite:///quran_dev.db"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///quran_dev.db"
    
    # Media Files
    MEDIA_ROOT: str = "/srv/quran-api/media"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # JWT
    JWT_SECRET: str = "jwt-secret-change-in-production"
    JWT_ACCESS_TTL: int = 900  # 15 minutes
    JWT_REFRESH_TTL: int = 2592000  # 30 days
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "60 per minute"
    RATE_LIMIT_AUTH: str = "10 per minute"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "UTC"
    SCHEDULER_REVIEW_TIME: str = "03:00"
    
    # API
    API_TITLE: str = "Quran Learning API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-grade Flask backend for Quran memorization app"
    OPENAPI_VERSION: str = "3.0.2"
    
    @classmethod
    def init_app(cls, app):
        """Initialize Flask app with configuration."""
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = "text"
    
    # Use SQLite for local development
    DATABASE_URL = "sqlite:///quran_dev.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///quran_dev.db"
    
    # Allow all origins in development
    CORS_ORIGINS = ["*"]


class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
    # Ensure these are set via environment variables
    SECRET_KEY = os.environ.get("SECRET_KEY", BaseConfig.SECRET_KEY)
    DATABASE_URL = os.environ.get("DATABASE_URL", BaseConfig.DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", BaseConfig.SQLALCHEMY_DATABASE_URI)
    JWT_SECRET = os.environ.get("JWT_SECRET", BaseConfig.JWT_SECRET)
    
    # Production CORS origins
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",") if os.environ.get("CORS_ORIGINS") else BaseConfig.CORS_ORIGINS


class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    DATABASE_URL = "sqlite:///:memory:"
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration based on environment."""
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"]) 