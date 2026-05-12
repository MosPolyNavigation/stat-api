from typing import Type, TypeVar, Generic, Optional, Callable, Any, Dict
from dataclasses import dataclass, field

from sqlalchemy.orm import DeclarativeBase

from app.graphql.core.permissions import Permission
from app.graphql.core.filters import BaseFilterInput
from app.graphql.core.ordering import BaseOrderByInput

# Типы для обобщения
M = TypeVar("M", bound=DeclarativeBase)  # SQLAlchemy модель
T = TypeVar("T")                         # GraphQL Strawberry тип
F = TypeVar("F", bound=BaseFilterInput)  # Filter Input


@dataclass
class ResourceConfig(Generic[M, T, F]):
    """
    Конфигурация ресурса для авто-генерации резолверов.
    """
    model: Type[M]
    graphql_type: Type[T]
    filter_input: Type[F]
    order_by_input: Type[BaseOrderByInput]
    convert: Callable[[M], T]
    permissions: "ResourcePermissions"

    # Пагинация
    cursor_field: str | list[str] = "id"
    cursor_separator: str = ":"
    page_size_default: int = 10

    # Валидация
    validators: Dict[str, Callable[[Any], bool | str]] = field(default_factory=dict)

    # 🔹 Глобальный флаг логирования (по умолчанию выключено)
    enable_logging: bool = False

    # 🔹 Флаги логирования по операциям
    enable_logging_list: Optional[bool] = None
    enable_logging_get: Optional[bool] = None
    enable_logging_create: Optional[bool] = None
    enable_logging_update: Optional[bool] = None
    enable_logging_delete: Optional[bool] = None

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
        specific_flag: Optional[bool] = getattr(self, flag_attr, None)
        if specific_flag is not None:
            return specific_flag

        # Если нет — используем глобальный флаг
        return self.enable_logging


@dataclass
class ResourcePermissions:
    """Набор разрешений для операций CRUD."""
    view: Optional[Permission] = None
    create: Optional[Permission] = None
    edit: Optional[Permission] = None
    delete: Optional[Permission] = None
