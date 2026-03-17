from datetime import datetime
from typing import Dict, Union
from collections import OrderedDict


class AppState:
    """
    Класс состояния приложения.
    
    Attributes:
        user_access: OrderedDict {
            user_id: {
                endpoint_key: datetime  # время последнего запроса к этому эндпоинту
            }
        }
    """
    user_access: OrderedDict[str, Dict[str, datetime]]
    
    def __init__(self, max_users: int = 10_000):
        self.user_access = OrderedDict()
        self._max_users = max_users