from pydantic import BaseModel, Field
from typing import Optional


class PermissionGrantInfo(BaseModel):
    """Информация о конкретном праве и возможности его делегирования"""
    right: str
    can_grant: bool


class UserOut(BaseModel):
    """Схема для возврата информации о пользователе"""
    id: int = Field(title="ID", description="User ID")
    login: str = Field(title="Login", description="User login")
    is_active: bool = Field(title="Is Active", description="Is user active or disabled")

    rights_by_goals: Optional[dict[str, list[PermissionGrantInfo]]] = Field(
        title="Rights by Goals",
        description="Права, сгруппированные по целям, с указанием возможности делегирования",
        default=None
    )
