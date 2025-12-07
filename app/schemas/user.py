"""Схемы для представления пользователей."""

from typing import Optional

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    """Данные пользователя, которые возвращаются наружу."""

    id: int = Field(title="id", description="User ID")
    login: str = Field(title="login", description="User login")
    is_active: bool = Field(title="is_active", description="Is user active or disabled")
    rights_by_goals: Optional[dict[str, list[str]]] = Field(
        title="rights_by_goals",
        description="Rights for goals",
        default=None,
    )


class UserUpdateResponse(BaseModel):
    """Ответ на обновление пользователя."""

    message: str = Field(description="Результат операции")
    user: UserOut


class UserDeleteResponse(BaseModel):
    """Ответ на удаление пользователя."""

    message: str = Field(description="Результат операции")
    user_id: int = Field(description="Удаленный пользователь")
