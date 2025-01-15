from pydantic import BaseModel, Field


class Status(BaseModel):
    """
    Класс для статуса выполнения запроса.

    Этот класс содержит поле, которое уточняет, каков статус выполнения отправленного запроса.

    Attributes:
        status: Статус процедуры.
    """
    status: str = Field(title="Procedure-status", description="Status of procedure", default="OK")
