"""Глобальные кеши приложения: графы и расписание."""

from typing import Dict, Union

from app.schemas import Graph
from app.schemas.rasp.schedule import Schedule

# Кеш графов навигации по кампусам.
global_graph: Dict[str, Graph] = {}
# Кеш расписания, загружаемого фоновой задачей.
global_rasp: Union[Schedule, None] = None
# Флаг, сигнализирующий о занятости фоновой задачи.
locker: bool = False
