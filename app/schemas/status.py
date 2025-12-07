"""Базовый ответ с сообщением о результате операции."""

from pydantic import BaseModel, Field


class Status(BaseModel):
    """Короткий статус операции без дополнительных данных."""

    status: str = Field(
        title="Procedure-status",
        description="Status of procedure",
        default="OK",
    )
