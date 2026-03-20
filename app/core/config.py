from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "Arena Event Hub"
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./arena_event_hub.db")


settings = Settings()
