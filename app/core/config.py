"""project settings"""
import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings(BaseSettings):
    database_url: str
    private_key_path: str
    public_key_path: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    email_password: str
    email_login: str
    redis_host: str
    redis_port: int
    mongo_url: str

    class Config:
        env_file = ".env"

settings = Settings()
# from app.core.config import settings