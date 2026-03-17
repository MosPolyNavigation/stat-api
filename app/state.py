from datetime import datetime
from typing import Dict, Union, List, Optional
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
    user_review_access: OrderedDict[
        str, 
        Dict[str, Union[List[datetime], bool, Optional[str], Optional[datetime], int]]
    ]
    
    def __init__(self, max_users: int = 1000):
        self.user_access = OrderedDict()
        self.user_review_access = OrderedDict()
        self._max_users = max_users