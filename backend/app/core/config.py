"""
Core configuration settings for Bravola Mini SaaS
"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from pathlib import Path

class Settings(BaseSettings):
    # Core Settings
    PROJECT_NAME: str = "Bravola Mini SaaS"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # ✅ FIX 1: Added missing variable that caused Login Crash
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    POSTGRES_SERVER: str = "postgres" 
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "bravola_db"
    DATABASE_URL: str = ""
    
    # ✅ FIX 2: Added missing variable that caused Database Crash
    DATABASE_ECHO: bool = False 

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: str, values: dict) -> str:
        if isinstance(v, str) and v:
            return v
        return str(f"postgresql+asyncpg://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@{values.get('POSTGRES_SERVER')}/{values.get('POSTGRES_DB')}")
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # CORS
    # ✅ FIX 3: Default allowed origins to fix "Network Error" / "CORS Blocked" on frontend
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return v
    
    # ML Models
    ML_ARTIFACTS_PATH: Path = Path(__file__).parent.parent.parent.parent / "ml_artifacts"
    MODEL_VERSION: str = "v1"
    
    # Optional Third Party
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""
    KLAVIYO_PUBLIC_KEY: str = ""
    KLAVIYO_PRIVATE_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()