"""Пользовательские исключения приложения."""


class LookupException(Exception):
    """Ошибка отсутствия сущности в базе."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"{self.name} not found"
