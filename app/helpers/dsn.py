"""Специализированные типы DSN для pydantic."""

from pydantic.networks import AnyUrl, UrlConstraints


class SqliteDsn(AnyUrl):
    """URL для подключения к SQLite (включая aiosqlite)."""

    _constraints = UrlConstraints(allowed_schemes=["sqlite", "sqlite+aiosqlite"])
