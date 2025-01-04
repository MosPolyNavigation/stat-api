from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, HttpUrl
from app.helpers.dsn import SqliteDsn
from functools import lru_cache


class Settings(BaseSettings):
    admin_key: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    sqlalchemy_database_url: SqliteDsn | PostgresDsn = SqliteDsn("sqlite:///app.db")
    allowed_hosts: set[HttpUrl] = set()
    allowed_methods: set[str] = set()

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings():
    return Settings()
