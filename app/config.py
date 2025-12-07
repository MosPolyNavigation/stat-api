"""Конфигурация приложения и загрузка переменных окружения."""

from functools import lru_cache
from typing import Annotated

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from app.helpers.dsn import SqliteDsn


class Settings(BaseSettings):
    """Настройки приложения, читаемые из переменных окружения или файла .env."""

    sqlalchemy_database_url: SqliteDsn | PostgresDsn = SqliteDsn("sqlite+aiosqlite:///app.db")
    static_files: str = "./static"
    allowed_hosts: Annotated[set[str], NoDecode] = ""
    allowed_methods: Annotated[set[str], NoDecode] = "*,"
    allowed_headers: Annotated[set[str], NoDecode] = "Authorization,"

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def decode_allowed_hosts(cls, raw: str) -> set[str]:
        """Разбирает список доменов из строки окружения в набор строк."""
        return {str(x.strip()) for x in raw.split(",") if x.strip()}

    @field_validator("allowed_methods", mode="before")
    @classmethod
    def decode_allowed_methods(cls, raw: str) -> set[str]:
        """Разбирает список HTTP-методов из строки окружения в набор строк."""
        return {str(x.strip()) for x in raw.split(",") if x.strip()}

    @field_validator("allowed_headers", mode="before")
    @classmethod
    def decode_allowed_headers(cls, raw: str) -> set[str]:
        """Разбирает список заголовков из строки окружения в набор строк."""
        return {str(x.strip()) for x in raw.split(",") if x.strip()}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Возвращает кешированный экземпляр настроек."""
    return Settings()
