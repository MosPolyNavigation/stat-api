import asyncio
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.schemas import Graph
from app.schemas.rasp.schedule import Schedule


class AppState:
    """
    Централизованное мутабельное состояние приложения.

    Заменяет модуль app.globals и обеспечивает корректную синхронизацию
    тяжёлых асинхронных операций через asyncio.Lock.

    Хранит:
        Rate limiter:
            user_access — частоты запросов на обычные эндпоинты;
            user_review_access — частоты и баны на эндпоинтах отзывов.
        Прикладные данные (раньше жили в app.globals):
            global_graph — графы навигации по локациям;
            global_rasp — текущее расписание;
            location_data_json — собранный JSON с данными локаций.
        Примитивы синхронизации:
            _rasp_lock — защита fetch_cur_rasp от параллельного запуска;
            _location_lock — защита fetch_location_data от параллельного запуска.
    """

    user_access: OrderedDict[str, Dict[str, datetime]]
    user_review_access: OrderedDict[
        str,
        Dict[str, Union[List[datetime], bool, Optional[str], Optional[datetime], int]]
    ]

    global_graph: Dict[str, Graph]
    global_rasp: Optional[Schedule]
    location_data_json: Optional[Dict[str, Any]]

    def __init__(self, max_users: int = 1000):
        self.user_access = OrderedDict()
        self.user_review_access = OrderedDict()
        self._max_users = max_users

        self.global_graph = {}
        self.global_rasp = None
        self.location_data_json = None

        self._rasp_lock = asyncio.Lock()
        self._location_lock = asyncio.Lock()

    def reset_for_tests(self) -> None:
        """Сбрасывает все коллекции и поля. Используется тестами для изоляции состояния между прогонами."""
        self.user_access.clear()
        self.user_review_access.clear()
        self.global_graph = {}
        self.global_rasp = None
        self.location_data_json = None
        self._rasp_lock = asyncio.Lock()
        self._location_lock = asyncio.Lock()
