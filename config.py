"""Runtime configuration loaded from the environment."""

from __future__ import annotations

import os
import sys
import logging
from typing import List, Set
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    BOT_USERNAME: str = Field(default="@AniUzAnimeBot", env="BOT_USERNAME")
    OWNER_ID: int = Field(..., env="OWNER_ID")
    ADMIN_IDS_RAW: str = Field(default="", env="ADMIN_IDS")
    MANDATORY_CHANNELS_RAW: str = Field(default="", env="MANDATORY_CHANNELS")
    POST_CHANNEL: str = Field(default="", env="POST_CHANNEL")
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///aniuz_bot.db", env="DATABASE_URL")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    @field_validator("BOT_TOKEN")
    def validate_token(cls, v: str) -> str:
        if not v or ":" not in v:
            raise ValueError("BOT_TOKEN noto'g'ri!")
        return v.strip()

    @property
    def admin_ids(self) -> Set[int]:
        ids = {self.OWNER_ID}
        if self.ADMIN_IDS_RAW:
            for item in self.ADMIN_IDS_RAW.split(","):
                if item.strip().isdigit():
                    ids.add(int(item.strip()))
        return ids

    @property
    def mandatory_channels(self) -> List[str]:
        if not self.MANDATORY_CHANNELS_RAW:
            return []
        return [ch.strip() for ch in self.MANDATORY_CHANNELS_RAW.split(",") if ch.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

try:
    config = Settings()
except Exception as e:
    print(f"❌ Xatolik: {e}")
    sys.exit(1)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger("aniuz_bot")
