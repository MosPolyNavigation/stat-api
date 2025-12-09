"""Глобальные кэши для графов навигации и расписаний."""

from .schemas import Graph
from typing import Dict, Union
from app.schemas.rasp.schedule import Schedule

global_graph: Dict[str, Graph] = dict()
global_rasp: Union[Schedule, None] = None
locker: bool = False
