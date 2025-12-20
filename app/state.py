"""Глобальное состояние приложения для учёта частоты запросов."""


class AppState:
    f"""
    Хранит отметки времени последнего обращения пользователя.

    Attributes:
        user_access: Словарь {{user_id: datetime последнего обращения}}.
    """

    def __init__(self):
        self.user_access = {}
