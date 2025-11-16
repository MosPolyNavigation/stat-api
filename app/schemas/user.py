from pydantic import BaseModel, Field
from typing import Optional


class UserOut(BaseModel):
    """Схема для возврата информации о пользователе"""

    id: int = Field(
        title="id",
        description="User ID"
    )
    login: str = Field(
        title="login",
        description="User login",
    )
    is_active: bool = Field(
        title="is_active",
        description="Is user active or disabled"
    )
    rights_by_goals: Optional[dict[str, list[str]]] = Field(
        title="rights_by_goals",
        description="Rights for goals",
        default=None
    )
