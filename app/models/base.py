"""Базовая декларативная модель SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Общий базовый класс для всех моделей."""

    pass
