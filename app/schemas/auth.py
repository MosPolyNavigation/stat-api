from typing import Optional
from pydantic import BaseModel, Field


class AuthScheme(BaseModel):
    """Схема входных данных для авторизации пользователя."""

    username: str = Field(
        title="username",
        description="Логин пользователя",
    )
    password: str = Field(
        title="password",
        description="Пароль пользователя",
    )
    scope: Optional[str] = Field(
        default=None,
        title="scope",
        description='Необязательный scope. Значение "long" включает выдачу refresh-токена',
    )
    user_ip: Optional[str] = Field(
        default=None,
        title="user_ip",
        description="IP-адрес или идентификатор клиента для мониторинга активных сессий",
    )