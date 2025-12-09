"""Чтение конфигурации приложения из переменных окружения и .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import PostgresDsn, field_validator
from app.helpers.dsn import SqliteDsn
from functools import lru_cache
from typing import Annotated


class Settings(BaseSettings):
    """
    Настройки приложения, читаемые из окружения или файла .env.

    Attributes:
        sqlalchemy_database_url: Строка подключения SQLAlchemy (sqlite или postgres).
        static_files: Каталог для статики и карт.
        allowed_hosts: Разрешенные источники для CORS.
        allowed_methods: Разрешенные HTTP-методы для CORS.
        allowed_headers: Разрешенные заголовки для CORS.

    Config:
        env_file: Имя файла .env.
        env_file_encoding: Кодировка файла .env.
    """

    sqlalchemy_database_url: SqliteDsn | PostgresDsn = SqliteDsn("sqlite+aiosqlite:///app.db")
    static_files: str = "./static"
    allowed_hosts: Annotated[set[str], NoDecode] = ""
    allowed_methods: Annotated[set[str], NoDecode] = "*,"
    allowed_headers: Annotated[set[str], NoDecode] = "Authorization,"

    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def decode_allowed_hosts(cls, v: str) -> set[str]:
        """Преобразует строку разрешенных хостов в множество."""
        return set([str(x.strip()) for x in v.split(',') if x.strip()])

    @field_validator('allowed_methods', mode='before')
    @classmethod
    def decode_allowed_methods(cls, v: str) -> set[str]:
        """Преобразует список методов в множество для CORS."""
        return set([str(x.strip()) for x in v.split(',') if x.strip()])

    @field_validator('allowed_headers', mode='before')
    @classmethod
    def decode_allowed_headers(cls, v: str) -> set[str]:
        """Преобразует строку заголовков в множество."""
        return set([str(x.strip()) for x in v.split(',') if x.strip()])

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


@lru_cache()
def get_settings():
    """
    Возвращает кэшированный экземпляр настроек приложения.

    Args:
        None

    Returns:
        Settings: Конфигурация приложения, считанная из окружения.
    """
    return Settings()
