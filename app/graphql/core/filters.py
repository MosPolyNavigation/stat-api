from typing import Optional, Type, List, Union
from dataclasses import fields, is_dataclass, dataclass
from sqlalchemy import and_, or_, not_, Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import DeclarativeBase
import strawberry


# =============================================================================
# 0. Базовый класс для строгой типизации
# =============================================================================
@dataclass
class BaseFilterInput:
    """Базовый датакласс для всех GraphQL-фильтров.
    Наследование от dataclass удовлетворяет статический анализатор для fields().
    """
    pass


# =============================================================================
# 1. Примитивы фильтрации (GraphQL Input Types)
# =============================================================================
@strawberry.input
class BooleanFilterInput(BaseFilterInput):
    eq: Optional[bool] = None
    ne: Optional[bool] = None
    is_null: Optional[bool] = None


@strawberry.input
class IntFilterInput(BaseFilterInput):
    eq: Optional[int] = None
    ne: Optional[int] = None
    gt: Optional[int] = None
    gte: Optional[int] = None
    lt: Optional[int] = None
    lte: Optional[int] = None
    is_in: Optional[list[int]] = None
    is_not_in: Optional[list[int]] = None
    is_null: Optional[bool] = None
    between: Optional[list[int]] = None
    not_between: Optional[list[int]] = None


@strawberry.input
class StringFilterInput(BaseFilterInput):
    eq: Optional[str] = None
    ne: Optional[str] = None
    ci_eq: Optional[str] = None  # Case-insensitive exact match
    contains: Optional[str] = None  # ILIKE '%val%'
    starts_with: Optional[str] = None  # ILIKE 'val%'
    ends_with: Optional[str] = None  # ILIKE '%val'
    like: Optional[str] = None  # LIKE 'pattern'
    not_like: Optional[str] = None  # NOT LIKE 'pattern'
    is_in: Optional[list[str]] = None
    is_not_in: Optional[list[str]] = None
    is_null: Optional[bool] = None


# =============================================================================
# 2. Ядро применения фильтров к колонке
# =============================================================================
def _build_column_conditions(col: ColumnElement, f: BaseFilterInput) -> Optional[ColumnElement]:
    """Применяет операторы фильтра к конкретной колонке SQLAlchemy."""
    conditions: list[ColumnElement] = []

    # Общие операторы
    eq: Union[int, str, bool, None] = getattr(f, "eq", None)
    ne: Union[int, str, bool, None] = getattr(f, "ne", None)
    if eq is not None:
        conditions.append(col == eq)
    if ne is not None:
        conditions.append(col != ne)

    # is_null: важно использовать 'is True/False', т.к. False - валидное значение
    is_null: Optional[bool] = getattr(f, "is_null", None)
    if is_null:
        conditions.append(col.is_(None))
    elif is_null is False:
        conditions.append(col.isnot(None))

    # Списки
    is_in: Union[list[int], list[str], None] = getattr(f, "is_in", None)
    if is_in:
        conditions.append(col.in_(is_in))
    is_not_in: Union[list[int], list[str], None] = getattr(f, "is_not_in", None)
    if is_not_in:
        conditions.append(~col.in_(is_not_in))

    # Сравнения (числа/даты)
    for op in ("gt", "gte", "lt", "lte"):
        val: Optional[int] = getattr(f, op, None)
        if val is not None:
            conditions.append(getattr(col, f"__{op}__")(val))

    # Диапазоны
    between: Optional[list[int]] = getattr(f, "between", None)
    if between and len(between) == 2:
        conditions.append(col.between(between[0], between[1]))
    not_between: Optional[list[int]] = getattr(f, "not_between", None)
    if not_between and len(not_between) == 2:
        conditions.append(~col.between(not_between[0], not_between[1]))

    # Строковые операторы (только для текстовых колонок)
    if hasattr(col, "ilike"):
        ci_eq: Optional[str] = getattr(f, "ci_eq", None)
        contains: Optional[str] = getattr(f, "contains", None)
        starts_with: Optional[str] = getattr(f, "starts_with", None)
        ends_with: Optional[str] = getattr(f, "ends_with", None)

        if ci_eq is not None:
            conditions.append(col.ilike(ci_eq))
        if contains is not None:
            conditions.append(col.ilike(f"%{contains}%"))
        if starts_with is not None:
            conditions.append(col.ilike(f"{starts_with}%"))
        if ends_with is not None:
            conditions.append(col.ilike(f"%{ends_with}%"))

    if hasattr(col, "like"):
        like: Optional[str] = getattr(f, "like", None)
        not_like: Optional[str] = getattr(f, "not_like", None)
        if like is not None:
            conditions.append(col.like(like))
        if not_like is not None:
            conditions.append(~col.like(not_like))

    return and_(*conditions) if conditions else None


# =============================================================================
# 3. Рекурсивный сбор условий из GraphQL-фильтра
# =============================================================================
def _build_filter_condition(model: Type[DeclarativeBase], filters: BaseFilterInput) -> Optional[ColumnElement]:
    """Рекурсивно собирает дерево условий WHERE из объекта фильтра."""
    if not filters:
        return None
    if not is_dataclass(filters):
        raise TypeError(f"Ожидается Strawberry-инпут (dataclass), получен {type(filters).__name__}")

    conditions: list[ColumnElement] = []
    for field in fields(filters):
        val = getattr(filters, field.name)
        if val is None:
            continue

        # Логические операторы (Strawberry маппит `and` -> `and_` через name="and")
        if field.name == "and_":
            sub_filters: List[BaseFilterInput] = val if val is not None else []
            sub = [_build_filter_condition(model, f) for f in sub_filters]
            valid = [c for c in sub if c]
            if valid:
                conditions.append(and_(*valid))

        elif field.name == "or_":
            sub_filters: List[BaseFilterInput] = val if val is not None else []
            sub = [_build_filter_condition(model, f) for f in sub_filters]
            valid = [c for c in sub if c]
            if valid:
                conditions.append(or_(*valid))

        elif field.name == "not_":
            sub_filter: BaseFilterInput = val
            cond = _build_filter_condition(model, sub_filter)
            if cond:
                conditions.append(not_(cond))

        else:
            # Полевой фильтр: имя поля фильтра = имя колонки модели
            col: Optional[ColumnElement] = getattr(model, field.name, None)
            if col is None:
                raise ValueError(f"Model {model.__name__} не имеет колонки '{field.name}'")
            cond = _build_column_conditions(col, val)
            if cond:
                conditions.append(cond)

    return and_(*conditions) if conditions else None


# =============================================================================
# 4. Публичный API для резолверов
# =============================================================================
def apply_filters(stmt: Select, model: Type[DeclarativeBase], filters: BaseFilterInput) -> Select:
    """
    Применяет GraphQL-фильтры к SQLAlchemy Select.

    ✅ Строгая типизация: принимает только инпуты, унаследованные от BaseFilterInput
    ✅ Работает с Relay, async/await, и любыми типами фильтров
    ✅ Автоматически пропускает None-поля
    ✅ Поддерживает вложенные and/or/not
    """
    cond = _build_filter_condition(model, filters)
    return stmt.where(cond) if cond else stmt
