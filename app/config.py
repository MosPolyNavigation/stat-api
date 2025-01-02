from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    admin_key: str = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    sqlalchemy_database_url: str = "sqlite:///app.db"

    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings():
    return Settings()
