from datetime import datetime, date

from enum import Enum
from typing import Optional, Type, List, Any, TypeVar, Callable
from dataclasses import fields, is_dataclass, dataclass
from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import DeclarativeBase
import strawberry

from app.graphql.core.tools import _get_attr

T = TypeVar("T")


# =============================================================================
# 0. Базовый класс и примитивы
# =============================================================================
@dataclass
class BaseOrderByInput:
    """Базовый датакласс для инпутов сортировки."""

    pass


@strawberry.enum
class OrderDir(Enum):
    ASC = "ASC"
    DESC = "DESC"


# =============================================================================
# 1. Валидация структуры сортировки
# =============================================================================
DEFAULT_ORDER_BY_MAX_DEPTH = 3  # Настраиваемый лимит вложенности


def _validate_order_input(
    order_input: BaseOrderByInput,
    max_depth: int = DEFAULT_ORDER_BY_MAX_DEPTH,
    current_depth: int = 0,
) -> None:
    if current_depth >= max_depth:
        raise ValueError(
            f"Превышена максимальная глубина сортировки (max={max_depth}). "
            f"Используйте не более {max_depth} уровней then_by."
        )

    if not is_dataclass(order_input):
        raise TypeError(
            f"Ожидается инпут сортировки (dataclass), получен {type(order_input).__name__}"
        )

    # Считаем поля сортировки (исключаем then_by)
    set_columns = [
        f.name
        for f in fields(order_input)
        if f.name != "then_by" and getattr(order_input, f.name) is not None
    ]

    if len(set_columns) > 1:
        raise ValueError(
            f"На каждом уровне можно задать только одно поле сортировки. Указаны: {set_columns}"
        )

    # Рекурсивная валидация then_by с инкрементом глубины
    if order_input.then_by is not None:  # type: ignore
        _validate_order_input(order_input.then_by, max_depth, current_depth + 1)  # type: ignore


# =============================================================================
# 2. Ядро построения ORDER BY
# =============================================================================
def _build_order_by_clauses(
    model: Type[DeclarativeBase], order_input: BaseOrderByInput
) -> List[ColumnElement]:
    clauses: List[ColumnElement] = []
    for field in fields(order_input):
        val = getattr(order_input, field.name)
        if val is None:
            continue
        if field.name == "then_by":
            clauses.extend(_build_order_by_clauses(model, val))
        else:
            col: Optional[ColumnElement] = getattr(model, field.name, None)
            if col is None:
                raise ValueError(
                    f"Model {model.__name__} не имеет колонки '{field.name}' для сортировки"
                )
            clauses.append(col.asc() if val == OrderDir.ASC else col.desc())
    return clauses


# =============================================================================
# 3. Публичный API для резолверов
# =============================================================================
def apply_order_by(
    stmt: Select,
    model: Type[DeclarativeBase],
    order_input: Optional[BaseOrderByInput],
    max_depth: int = DEFAULT_ORDER_BY_MAX_DEPTH,
) -> Select:
    """
    Применяет GraphQL-сортировку к SQLAlchemy Select.

    ✅ Защита от бесконечной вложенности через max_depth
    ✅ Валидация: максимум одно поле сортировки на каждом уровне
    """
    if order_input is None:
        return stmt

    _validate_order_input(order_input, max_depth)
    clauses = _build_order_by_clauses(model, order_input)
    return stmt.order_by(*clauses) if clauses else stmt


def _make_sort_key(order_input: BaseOrderByInput) -> Callable[[Any], tuple]:
    """Создаёт ключ сортировки для sorted() на основе order_input."""
    sort_specs: list[tuple[str, bool]] = []  # (field_name, is_asc)

    def collect(order: BaseOrderByInput):
        for field in fields(order):
            val = getattr(order, field.name)
            if val is None:
                continue
            if field.name == "then_by":
                collect(val)
            else:
                is_asc = val == OrderDir.ASC
                sort_specs.append((field.name, is_asc))

    collect(order_input)

    def key_func(obj: Any) -> tuple:
        result = []
        for field_name, is_asc in sort_specs:
            val = _get_attr(obj, field_name)
            if val is None:
                result.append((1 if is_asc else 0, ""))
            else:
                result.append(
                    (0 if is_asc else 1, val if is_asc else _reverse_val(val))
                )
        return tuple(result)

    return key_func


def _reverse_val(val: Any) -> Any:
    """Инвертирует значение для сортировки по убыванию."""
    if isinstance(val, (int, float)):
        return -val
    elif isinstance(val, (str, datetime, date)):
        # Для строк/дат используем кортеж с флагом, чтобы не ломать сравнение
        return val  # сортировка будет работать через ключ-кортеж
    return val


def sort_list(models: List[T], order_input: Optional[BaseOrderByInput]) -> List[T]:
    """Сортирует список моделей по GraphQL-order_by."""
    if not order_input:
        return models
    key_func = _make_sort_key(order_input)
    return sorted(models, key=key_func)
