"""Схемы фиксации смены плана корпуса."""

from pydantic import BaseModel, Field


class ChangePlanBase(BaseModel):
    """Данные о переключении плана пользователем."""

    user_id: str = Field(
        title="id",
        description="Unique user id",
        min_length=36,
        max_length=36,
        pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}",
    )
    plan_id: str = Field(
        title="Changed-plan",
        description="Changed plan by user",
        max_length=50,
        min_length=1,
    )


class ChangePlanIn(ChangePlanBase):
    """Входная модель для сохранения факта смены плана."""

    pass
