from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-1.5-flash")
    data_path: Path = Field(
        default=Path(__file__).parent.parent / "data" / "faq.csv",
        env=["DATA_PATH", "CSV_PATH"],
    )
    max_context_rows: int = Field(default=3, ge=1, le=10)
    default_language: Literal["fr", "ar"] = "fr"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

