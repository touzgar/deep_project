import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Smart Face Attendance System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://admin:adminpassword@localhost:5432/attendance_db"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production-use-openssl-rand-hex-32")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:80",
    ]
    
    # UploadThing Configuration (Optional)
    UPLOADTHING_TOKEN: Optional[str] = os.getenv("UPLOADTHING_TOKEN", "")
    UPLOADTHING_APP_ID: Optional[str] = os.getenv("UPLOADTHING_APP_ID", "")
    UPLOADTHING_SECRET: Optional[str] = os.getenv("UPLOADTHING_SECRET", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
