"""
Centralized app configuration, loaded from environment variables / .env.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Graduate Skill Gap Prediction System"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./skillgap.db"

    secret_key: str = "insecure-dev-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    allowed_origins: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:5501,http://127.0.0.1:5501"

    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-3.6-flash"

    upload_dir: str = "./uploads"
    max_upload_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
