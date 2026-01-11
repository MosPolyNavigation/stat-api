from datetime import datetime
from pydantic import BaseModel, Field


class TgBotEventBase(BaseModel):
    """
    Базовая схема для событий телеграм-бота.

    Attributes:
        tg_id: Telegram ID пользователя;
        event_type: Название типа события;
        time: Время возникновения события;
        is_dod: Флаг, что событие относится к ДОД-боту.
    """
    tg_id: int = Field(
        title="Telegram ID",
        description="Идентификатор пользователя Telegram",
        ge=1
    )
    event_type: str = Field(
        title="Тип события",
        description="Название типа события, отправленного ботом",
        min_length=1,
        max_length=100
    )
    time: datetime = Field(
        title="Время события",
        description="Метка времени события"
    )
    is_dod: bool = Field(
        title="ДОД-бот",
        description="Признак, что событие относится к боту для ДОД"
    )


class TgBotEventIn(TgBotEventBase):
    """
    Схема входных данных для создания записи о событии телеграм-бота.
    """
    pass
