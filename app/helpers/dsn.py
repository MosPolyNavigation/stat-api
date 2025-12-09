"""Расширение типов Pydantic для поддержки SQLite DSN."""

from pydantic.networks import AnyUrl, UrlConstraints


class SqliteDsn(AnyUrl):
    """
    Валидирует DSN для SQLite и SQLite+aiosqlite.

    Attributes:
        _constraints: Допустимые схемы подключения.
    """

    _constraints = UrlConstraints(allowed_schemes=['sqlite', 'sqlite+aiosqlite'])
