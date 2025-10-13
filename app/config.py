from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import PostgresDsn, HttpUrl, field_validator
from app.helpers.dsn import SqliteDsn
from functools import lru_cache
from typing import Annotated


class Settings(BaseSettings):
    """
    Класс настроек приложения.

    Этот класс содержит настройки приложения,
    которые могут быть загружены из файла .env.

    Attributes:
        admin_key: Административный ключ.
        sqlalchemy_database_url: URL базы данных SQLAlchemy.
        allowed_hosts: Разрешенные хосты.
        allowed_methods: Разрешенные методы.

    Config:
        env_file: Путь к файлу .env.
        env_file_encoding: Кодировка файла .env.
    """
    admin_key: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    sqlalchemy_database_url: SqliteDsn | PostgresDsn = SqliteDsn("sqlite:///app.db")
    static_files: str = "./static"
    allowed_hosts: Annotated[set[str], NoDecode] = ""
    allowed_methods: Annotated[set[str], NoDecode] = "PUT,POST,GET"

    @field_validator('allowed_hosts', mode='before')
    @classmethod
    def decode_allowed_hosts(cls, v: str) -> set[str]:
        return set([str(x.strip()) for x in v.split(',') if x.strip()])

    @field_validator('allowed_methods', mode='before')
    @classmethod
    def decode_allowed_methods(cls, v: str) -> set[str]:
        return set([str(x.strip()) for x in v.split(',') if x.strip()])

    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )


@lru_cache()
def get_settings():
    """
    Функция для получения настроек приложения.

    Эта функция возвращает объект настроек приложения.
    Она использует декоратор lru_cache для кэширования результатов.

    Returns:
        Settings: Объект настроек приложения.
    """
    return Settings()
