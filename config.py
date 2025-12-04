"""
config.py
Loads .env variables and exposes structured settings object.
"""

from pydantic import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    DATABASE_URL: str

    TRIAL_MONTHS: int = 4   # default 4 months
    AUTO_PAY_ENABLE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate
settings = Settings()

print("Admin IDs loaded:", settings.ADMIN_IDS)