from pydantic_core import core_schema
from pydantic import BaseModel
from typing import Optional
from . import PlanData

class RoomData(BaseModel):
    id: str
    type: Optional["RoomType"]
    available: bool
    title: str
    subTitle: str
    icon: str
    plan: Optional[PlanData]


class RoomType(str):
    allowed_values = frozenset({
        "Пока не известно",
        "Лифт",
        "Лестница",
        "Переход между корпусами",
        "Учебная аудитория",
        "Лекторий",
        "Лаборатория",
        "Общественное пространство / актовый или концертный зал",
        "Коворкинг",
        "Администрация",
        "Вход в здание",
        "Приёмная комиссия",
        "Женский туалет",
        "Мужской туалет",
        "Общий туалет",
        "Столовая / кафе",
        "Библиотека / читальный зал",
        "Клуб / секция / внеучебка",
        "Спортивный зал",
        "Гардероб / раздевалка",
        "Не используется",
        "Служебное помещение"
    })

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _a, _b
    ) -> core_schema.CoreSchema:
        def validate(value: str) -> RoomType:
            if value not in cls.allowed_values:
                raise ValueError(
                    f"Invalid value '{value}'. Allowed: {sorted(cls.allowed_values)}"
                )
            return cls(value)
        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema(),
        )
