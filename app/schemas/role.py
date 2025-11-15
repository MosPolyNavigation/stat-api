from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class RoleOut(BaseModel):
    """Схема для возврата информации о роли"""

    id: int = Field(
        title="id",
        description="Идентификатор роли"
    )

    name: str = Field(
        title="name",
        description="Название роли"
    )

    rights_by_goals: Optional[Dict[str, List[str]]] = Field(
        title="rights_by_goals",
        description="Правила доступа: цель - список прав",
        default=None
    )
