"""project settings"""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(".env")

class Settings(BaseSettings):
    database_url: str
    private_key_path: str
    public_key_path: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
# from app.core.config import settings