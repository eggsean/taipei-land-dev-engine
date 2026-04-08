from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./land_dev.db"
    api_v1_prefix: str = "/api/v1"
    rule_version: str = "2025.04.01"

    model_config = {"env_prefix": "LAND_DEV_"}


settings = Settings()
