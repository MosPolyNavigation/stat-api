import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Self, Optional, Literal

import yaml
from pydantic import BaseModel, PostgresDsn, model_validator, ConfigDict, Field

from app.helpers.dsn import SqliteDsn

BASE_DIR = Path(__file__).resolve().parent.parent

# Паттерн: {{ env("VAR_NAME", "default") }} или {{ env("VAR_NAME") }}
_ENV_PATTERN = re.compile(r'\{\{\s*env\("([^"]+)"(?:\s*,\s*"([^"]*)"\s*)?\)\s*\}\}')


# ─── Загрузка .env без перезаписи системных переменных ────────────────────────

def _load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    with open(dotenv_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


# ─── Подстановка переменных окружения в YAML-строку ───────────────────────────

def _substitute_env(raw: str) -> str:
    def replacer(match: re.Match) -> str:
        var_name = match.group(1)
        default = match.group(2)
        value = os.environ.get(var_name)
        if value is not None:
            return value
        if default is not None:
            return default
        return ""

    return _ENV_PATTERN.sub(replacer, raw)


# ─── Pydantic-модели конфигурации ─────────────────────────────────────────────

class CronConfig(BaseModel):
    minute: str | int = "*"
    hour: str | int = "*"
    day: str | int = "*"
    month: str | int = "*"
    day_of_week: str | int = "*"
    timezone: str = "UTC"


class IntervalConfig(BaseModel):
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class SchedulerConfig(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    replace_existing: bool = False
    max_instances: int = 1
    misfire_grace_time: Optional[int] = None
    coalesce: bool = False


class JobConfig(BaseModel):
    name: str
    enabled: bool = True
    desc: str = ""
    trigger: Literal["cron", "interval"]
    cron: Optional[CronConfig] = None
    interval: Optional[IntervalConfig] = None
    scheduler: SchedulerConfig = SchedulerConfig()


class JobsConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    queue: str = "sqlite"
    url: str = "queue.db"
    # В YAML-конфиге ключ называется "list", но "list" — имя встроенного типа Python
    tasks: list[JobConfig] = Field(default=[], alias="list")


class CorsConfig(BaseModel):
    allowed_hosts: list[str] = []
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["Authorization"]


class StaticFileConfig(BaseModel):
    path: str
    name: str
    fallback: bool = False
    fallback_to: str | None = None

    @model_validator(mode="after")
    def validate_fallback_pair(self) -> Self:
        if self.fallback and self.fallback_to is None:
            raise ValueError("При fallback=True поле 'fallback_to' обязательно")
        if self.fallback_to is not None and not self.fallback:
            raise ValueError("Поле 'fallback_to' допустимо только при fallback=True")
        return self


class StaticConfig(BaseModel):
    base_path: str = "./static"
    files: list[StaticFileConfig] = []


class CompressionConfig(BaseModel):
    enable: bool = True


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int = 8080
    cors: CorsConfig | None = None
    static: StaticConfig | None = None
    compression: CompressionConfig | None = None


class DatabaseConfig(BaseModel):
    uri: SqliteDsn | PostgresDsn


class JwtTokenConfig(BaseModel):
    secret: str = "example1"
    expiration: int = 900


class JwtRefreshConfig(BaseModel):
    secret: str = "example2"
    expiration: int = 2592000
    cookie_name: str = "refresh_token"


class JwtConfig(BaseModel):
    access: JwtTokenConfig = JwtTokenConfig()
    refresh: JwtRefreshConfig = JwtRefreshConfig()


class Settings(BaseModel):
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig
    jwt: JwtConfig = JwtConfig()
    jobs: JobsConfig = JobsConfig()

    # ── Свойства для обратной совместимости ───────────────────────────────────

    @property
    def sqlalchemy_database_url(self) -> SqliteDsn | PostgresDsn:
        return self.database.uri

    @property
    def static_files(self) -> str:
        if self.server.static:
            return self.server.static.base_path
        return "./static"

    @property
    def allowed_hosts(self) -> list[str]:
        if self.server.cors:
            return self.server.cors.allowed_hosts
        return []

    @property
    def allowed_methods(self) -> list[str]:
        if self.server.cors:
            return self.server.cors.allowed_methods
        return ["*"]

    @property
    def allowed_headers(self) -> list[str]:
        if self.server.cors:
            return self.server.cors.allowed_headers
        return ["Authorization"]

    @property
    def access_secret(self) -> str:
        return self.jwt.access.secret

    @property
    def refresh_secret(self) -> str:
        return self.jwt.refresh.secret

    @property
    def access_duration(self) -> int:
        return self.jwt.access.expiration

    @property
    def refresh_duration(self) -> int:
        return self.jwt.refresh.expiration


# ─── Загрузка конфигурации ────────────────────────────────────────────────────

def load_settings() -> Settings:
    # [1] Определяем путь к конфигу
    config_path = Path(os.getenv("STATAPI_CONFIG", "config.yaml"))
    if not config_path.is_absolute():
        config_path = BASE_DIR / config_path

    if not config_path.exists():
        raise FileNotFoundError(
            f"Файл конфигурации не найден: {config_path}\n"
            "Создайте config.yaml из config.example.yaml и укажите путь через STATAPI_CONFIG."
        )

    # [2] Загружаем .env без перезаписи системных переменных
    _load_dotenv(BASE_DIR / ".env")

    # [3] Читаем YAML и подставляем {{ env(...) }}
    raw_yaml = config_path.read_text(encoding="utf-8")
    substituted = _substitute_env(raw_yaml)

    # [4] Парсим YAML
    data = yaml.safe_load(substituted) or {}

    # [5] Валидируем через Pydantic
    try:
        settings = Settings.model_validate(data)
    except Exception as exc:
        print(f"ОШИБКА: Некорректная конфигурация: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    # [6] Проверяем обязательное поле database.uri
    if not settings.database.uri:
        print(
            "ОШИБКА: database.uri обязателен, но не задан. "
            "Укажите его в config.yaml или через переменную окружения STATAPI_DB_URL.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    return settings


@lru_cache()
def get_settings() -> Settings:
    return load_settings()
