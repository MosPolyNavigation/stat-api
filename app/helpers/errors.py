"""Пользовательские исключения приложения."""


class LookupException(Exception):
    """
    Исключение, поднимаемое при отсутствии запрошенной сущности.

    Attributes:
        name: Имя сущности, которая не была найдена.
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name} not found"
