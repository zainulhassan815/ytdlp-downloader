from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Redis configuration
    redis_url: str = Field(alias="REDIS_URL")

    # PostgreSQL configuration (Neon)
    database_url: str = Field(alias="DATABASE_URL")

    # Celery configuration
    celery_broker_url: str = Field(alias="CELERY_BROKER_URL", default="")
    celery_result_backend: str = Field(alias="CELERY_RESULT_BACKEND", default="")

    # Download configuration
    download_dir: str = Field(alias="DOWNLOAD_DIR", default="/tmp/downloads")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url


settings = Settings()
