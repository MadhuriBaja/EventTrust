"""Application core configuration."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EventTrust API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"

    serpapi_api_key: str = ""
    frontend_origin: str = "http://localhost:3000"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()