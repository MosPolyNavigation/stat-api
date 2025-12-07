"""Схемы для описания ролей и результатов операций над ними."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RoleOut(BaseModel):
    """Описание роли с набором прав по целям."""

    id: int = Field(title="id", description="Идентификатор роли")
    name: str = Field(title="name", description="Название роли")
    rights_by_goals: Optional[Dict[str, List[str]]] = Field(
        title="rights_by_goals",
        description="Права, сгруппированные по целям: {goal: [right1, right2]}",
        default=None,
    )


class RoleActionResponse(BaseModel):
    """Результат операций удаления/создания связей роли."""

    message: str
    role_id: int


class RoleAssignmentResponse(BaseModel):
    """Результат привязки или отвязки роли от пользователя."""

    message: str
    user_id: int
    role_id: int
