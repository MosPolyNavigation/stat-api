from enum import Enum
from typing import Optional, Type, List
from dataclasses import fields, is_dataclass, dataclass
from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import DeclarativeBase
import strawberry


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
    current_depth: int = 0
) -> None:
    if current_depth >= max_depth:
        raise ValueError(
            f"Превышена максимальная глубина сортировки (max={max_depth}). "
            f"Используйте не более {max_depth} уровней then_by."
        )

    if not is_dataclass(order_input):
        raise TypeError(f"Ожидается инпут сортировки (dataclass), получен {type(order_input).__name__}")

    # Считаем поля сортировки (исключаем then_by)
    set_columns = [f.name for f in fields(order_input) if
                   f.name != "then_by" and getattr(order_input, f.name) is not None]

    if len(set_columns) > 1:
        raise ValueError(f"На каждом уровне можно задать только одно поле сортировки. Указаны: {set_columns}")

    # Рекурсивная валидация then_by с инкрементом глубины
    if order_input.then_by is not None:  # type: ignore
        _validate_order_input(order_input.then_by, max_depth, current_depth + 1)  # type: ignore


# =============================================================================
# 2. Ядро построения ORDER BY
# =============================================================================
def _build_order_by_clauses(model: Type[DeclarativeBase], order_input: BaseOrderByInput) -> List[ColumnElement]:
    clauses: List[ColumnElement] = []
    for field in fields(order_input):
        val = getattr(order_input, field.name)
        if val is None:
            continue
        if field.name == "then_by":
            clauses.extend(_build_order_by_clauses(model, val))
        else:
            col = getattr(model, field.name, None)
            if col is None:
                raise ValueError(f"Model {model.__name__} не имеет колонки '{field.name}' для сортировки")
            clauses.append(col.asc() if val == OrderDir.ASC else col.desc())  # noqa
    return clauses


# =============================================================================
# 3. Публичный API для резолверов
# =============================================================================
def apply_order_by(
    stmt: Select,
    model: Type[DeclarativeBase],
    order_input: Optional[BaseOrderByInput],
    max_depth: int = DEFAULT_ORDER_BY_MAX_DEPTH
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
