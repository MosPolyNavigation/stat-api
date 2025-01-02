from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn
from app.dsn import SqliteDsn
from functools import lru_cache


class Settings(BaseSettings):
    admin_key: str = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    sqlalchemy_database_url: SqliteDsn | PostgresDsn = SqliteDsn("sqlite:///app.db")
    allowed_hosts: set[str] = set()

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings():
    return Settings()
