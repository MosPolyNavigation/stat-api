from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    admin_key: str = "1234567890abcdef"
    sqlalchemy_database_url: str = "sqlite:///app.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
