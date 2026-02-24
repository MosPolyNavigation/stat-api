from .schemas import Graph
from typing import Dict, Union, Any, Optional
from app.schemas.rasp.schedule import Schedule

global_graph: Dict[str, Graph] = dict()
global_rasp: Union[Schedule, None] = None
locker: bool = False

location_data_json: Optional[Dict[str, Any]] = None
location_data_locker: bool = False
