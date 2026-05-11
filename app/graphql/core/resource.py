from typing import Type, TypeVar, Generic, Optional, Callable, Dict, Any
from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase

from app.graphql.core.permissions import Permission
from app.graphql.core.filters import BaseFilterInput
from app.graphql.core.ordering import BaseOrderByInput

# Типы для обобщения
M = TypeVar("M", bound=DeclarativeBase)  # SQLAlchemy модель
T = TypeVar("T")  # GraphQL Strawberry тип
F = TypeVar("F", bound=BaseFilterInput)  # Filter Input
C = TypeVar("C", bound=Callable[[M], T]) # Конвертер модель → тип


@dataclass
class ResourceConfig(Generic[M, T, F]):
    """
    Конфигурация ресурса для авто-генерации резолверов.
    """
    model: Type[M]
    graphql_type: Type[T]
    filter_input: Type[F]
    order_by_input: Type[BaseOrderByInput]
    convert: C
    permissions: "ResourcePermissions"

    # Пагинация
    cursor_field: str | list[str] = "id"
    cursor_separator: str = ":"

    page_size_default: int = 10

    # Валидация
    validators: Dict[str, Callable[[Any], bool | str]] = None

    # 🔹 Глобальный флаг логирования (по умолчанию выключено)
    enable_logging: bool = False

    # 🔹 Флаги логирования по операциям (переопределяют enable_logging)
    enable_logging_list: Optional[bool] = None  # для event_types
    enable_logging_get: Optional[bool] = None  # для event_type
    enable_logging_create: Optional[bool] = None  # для create_event_type
    enable_logging_update: Optional[bool] = None  # для update_event_type
    enable_logging_delete: Optional[bool] = None  # для delete_event_type

    def __post_init__(self):
        if self.validators is None:
            self.validators = {}

    # 🔹 Хелпер: решает, нужно ли логировать конкретную операцию
    def should_log(self, operation: str) -> bool:
        """
        Определяет, нужно ли логировать операцию.

        Args:
            operation: "list" | "get" | "create" | "update" | "delete"

        Returns:
            True, если логирование включено для этой операции.
        """
        # Сначала смотрим специфичный флаг
        flag_attr = f"enable_logging_{operation}"
        specific_flag = getattr(self, flag_attr, None)
        if specific_flag is not None:
            return specific_flag  # type: ignore

        # Если нет — используем глобальный флаг
        return self.enable_logging


@dataclass
class ResourcePermissions:
    """Набор разрешений для операций CRUD."""
    view: Optional[Permission] = None
    create: Optional[Permission] = None
    edit: Optional[Permission] = None
    delete: Optional[Permission] = None
