import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Face Attendance System"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://neondb_owner:npg_hMtrjxz9qA5C@ep-green-pine-anw2pzja-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b39a485a-063a-44e2-8b43-4ed04f7f2b9")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # UploadThing Configuration
    uploadthing_token: str = ""
    uploadthing_app_id: str = ""
    uploadthing_secret: str = ""
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
