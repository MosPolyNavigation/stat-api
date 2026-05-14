from typing import Optional, Type, List, Union, TypeVar, Any
from dataclasses import fields, is_dataclass, dataclass
from sqlalchemy import and_, or_, not_, Select
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import DeclarativeBase
import strawberry

from app.graphql.core.tools import _get_attr, _compare_values

T = TypeVar("T")


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
    op_map = {"gt": "__gt__", "gte": "__ge__", "lt": "__lt__", "lte": "__le__"}
    for op, sa_op in op_map.items():
        val = getattr(f, op, None)
        if val is not None:
            conditions.append(getattr(col, sa_op)(val))

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
            valid = [c for c in sub if c is not None]
            if valid:
                conditions.append(and_(*valid))

        elif field.name == "or_":
            sub_filters: List[BaseFilterInput] = val if val is not None else []
            sub = [_build_filter_condition(model, f) for f in sub_filters]
            valid = [c for c in sub if c is not None]
            if valid:
                conditions.append(or_(*valid))

        elif field.name == "not_":
            sub_filter: BaseFilterInput = val
            cond = _build_filter_condition(model, sub_filter)
            if cond is not None:
                conditions.append(not_(cond))

        else:
            # Полевой фильтр: имя поля фильтра = имя колонки модели
            col: Optional[ColumnElement] = getattr(model, field.name, None)
            if col is None:
                raise ValueError(f"Model {model.__name__} не имеет колонки '{field.name}'")
            cond = _build_column_conditions(col, val)
            if cond is not None:
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
    return stmt.where(cond) if cond is not None else stmt


def _apply_field_filter(model_instance: Any, field_name: str, filter_input: BaseFilterInput) -> bool:
    """Применяет условия фильтра к конкретному полю модели."""
    val = _get_attr(model_instance, field_name)

    # Общие операторы
    eq = getattr(filter_input, "eq", None)
    ne = getattr(filter_input, "ne", None)
    if eq is not None and not _compare_values(val, "eq", eq):
        return False
    if ne is not None and not _compare_values(val, "ne", ne):
        return False

    # is_null
    is_null = getattr(filter_input, "is_null", None)
    if is_null is True and val is not None:
        return False
    if is_null is False and val is None:
        return False

    # Списки
    is_in = getattr(filter_input, "is_in", None)
    if is_in is not None and not _compare_values(val, "in", is_in):
        return False
    is_not_in = getattr(filter_input, "is_not_in", None)
    if is_not_in is not None and not _compare_values(val, "not_in", is_not_in):
        return False

    # Сравнения
    for op in ("gt", "gte", "lt", "lte"):
        cmp_val = getattr(filter_input, op, None)
        if cmp_val is not None and not _compare_values(val, op, cmp_val):
            return False

    # Диапазоны
    between: Optional[List[Any]] = getattr(filter_input, "between", None)
    if between and len(between) == 2 and not _compare_values(val, "between", between):
        return False
    not_between: Optional[List[Any]] = getattr(filter_input, "not_between", None)
    if not_between and len(not_between) == 2 and not _compare_values(val, "not_between", not_between):
        return False

    # Строковые операторы (только если значение — строка)
    if isinstance(val, (str, type(None))):
        for op, attr in [("ci_eq", "eq"), ("contains", "contains"),
                         ("starts_with", "starts_with"), ("ends_with", "ends_with")]:
            cmp_val = getattr(filter_input, attr, None)
            if cmp_val is not None and not _compare_values(val, op, cmp_val):
                return False
        like = getattr(filter_input, "like", None)
        if like is not None and not _compare_values(val, "like", like):
            return False
        not_like = getattr(filter_input, "not_like", None)
        if not_like is not None and not _compare_values(val, "not_like", not_like):
            return False

    return True


def _matches_filter(model_instance: Any, model_type: Type, filters: BaseFilterInput) -> bool:
    """Рекурсивно проверяет, соответствует ли экземпляр модели условиям фильтра."""
    if not filters or not is_dataclass(filters):
        return True

    for field in fields(filters):
        val = getattr(filters, field.name)
        if val is None:
            continue

        # Логические операторы
        if field.name == "and_":
            sub_filters: List[BaseFilterInput] = val or []
            if not all(_matches_filter(model_instance, model_type, f) for f in sub_filters):
                return False
        elif field.name == "or_":
            sub_filters: List[BaseFilterInput] = val or []
            if not any(_matches_filter(model_instance, model_type, f) for f in sub_filters):
                return False
        elif field.name == "not_":
            if _matches_filter(model_instance, model_type, val):
                return False
        else:
            # Полевой фильтр
            if not _apply_field_filter(model_instance, field.name, val):
                return False
    return True


def filter_list(
        models: List[T],
        model_type: Type,
        filters: Optional[BaseFilterInput]
) -> List[T]:
    """Фильтрует список моделей по GraphQL-фильтру."""
    if not filters:
        return models
    return [m for m in models if _matches_filter(m, model_type, filters)]
