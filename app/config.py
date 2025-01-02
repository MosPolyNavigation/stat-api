from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    admin_key: str = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    sqlalchemy_database_url: str = "sqlite:///app.db"
    # allowed_hosts: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings():
    return Settings()
