"""
config.py - Settings loader
"""
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []
    DATABASE_URL: str
    TRIAL_MONTHS: int = 4
    AUTO_PAY_ENABLE: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
