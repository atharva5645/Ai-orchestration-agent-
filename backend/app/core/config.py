from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "Financial Deep Research Agent"
    environment: str = "development"
    log_level: str = "info"

    # API Keys
    google_api_key: Optional[str] = None
    google_api_key_2: Optional[str] = None
    google_api_key_3: Optional[str] = None
    google_api_key_4: Optional[str] = None
    google_api_key_5: Optional[str] = None
    google_api_key_6: Optional[str] = None
    tavily_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env.dev", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
