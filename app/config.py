from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, HttpUrl
from app.helpers.dsn import SqliteDsn
from functools import lru_cache


class Settings(BaseSettings):
    """
    Класс настроек приложения.

    Этот класс содержит настройки приложения, которые могут быть загружены из файла .env.

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
    allowed_hosts: set[HttpUrl] = set()
    allowed_methods: set[str] = set(["PUT", "POST", "GET"])

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


@lru_cache()
def get_settings():
    """
    Функция для получения настроек приложения.

    Эта функция возвращает объект настроек приложения. Она использует декоратор lru_cache для кэширования результатов.

    Returns:
        Settings: Объект настроек приложения.
    """
    return Settings()
