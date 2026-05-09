from typing import Optional, Type, TypeVar, Callable, List, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import and_, or_
from strawberry.relay.utils import from_base64

M = TypeVar("M", bound=DeclarativeBase)
T = TypeVar("T")


async def fetch_relay_page(
        session: AsyncSession,
        stmt: Select,
        *,
        first: Optional[int] = None,
        after: Optional[str] = None,
        model: Type[M],
        cursor_fields: Union[str, List[str]] = "id",
        convert: Callable[[M], T],
        cursor_separator: str = ":",  # Для составных ключей: "1:2"
) -> List[T]:
    """
    Универсальный хелпер для Relay-пагинации с SQLAlchemy.

    🔹 Поддерживает простые и составные ключи курсора
    🔹 Применяет фильтрацию на уровне БД (WHERE ... > cursor)
    🔹 Запрашивает first + 1 записей для определения has_next_page
    🔹 Возвращает список конвертированных GraphQL-типов

    Примеры:
        # Простой ключ
        await fetch_relay_page(..., cursor_fields="id", ...)

        # Составной ключ (лексикографическое сравнение)
        await fetch_relay_page(..., cursor_fields=["event_type_id", "payload_type_id"], ...)

        # Строковый ключ
        await fetch_relay_page(..., cursor_fields="ident", ...)

    Args:
        session: Async SQLAlchemy session
        stmt: Select-запрос с корректным ORDER BY
        first: Максимальное количество записей
        after: Base64-кодированный курсор
        model: SQLAlchemy модель
        cursor_fields: Имя поля или список полей для курсорной фильтрации
        convert: Функция конвертации модели → GraphQL-тип
        cursor_separator: Разделитель для составных курсоров (по умолчанию ":")

    Returns:
        List[GraphQLType] длиной <= first
    """
    # Нормализуем cursor_fields в список
    fields = [cursor_fields] if isinstance(cursor_fields, str) else cursor_fields

    # Применяем курсорную фильтрацию
    if after and fields:
        try:
            _, raw_cursor = from_base64(after)
            cursor_values = _parse_cursor_values(raw_cursor, fields, cursor_separator)
            stmt = _apply_cursor_filter(stmt, model, fields, cursor_values)
        except Exception:
            # Неверный курсор — игнорируем и начинаем с начала
            pass

    # Запрашиваем first + 1 для определения has_next_page
    limit = (first or 100) + 1
    stmt = stmt.limit(limit)

    # Выполняем запрос
    result = await session.execute(stmt)
    items = list(result.scalars().all())

    # Обрезаем лишний элемент
    if len(items) > (first or 100):
        items = items[:(first or 100)]

    # Конвертируем модели в типы
    return [convert(item) for item in items]


def _parse_cursor_values(raw_cursor: str, fields: List[str], separator: str) -> List[Any]:
    """
    Парсит сырой курсор в список значений для каждого поля.

    Примеры:
        "123" → [123]  (одно поле)
        "1:2" → [1, 2]  (два поля, разделитель ":")
        "user:admin" → ["user", "admin"]  (строковые поля)
    """
    if len(fields) == 1:
        # Простой ключ: пробуем int, иначе строка
        return [_coerce_cursor_type(raw_cursor)]

    # Составной ключ: разделяем по разделителю
    parts = raw_cursor.split(separator)
    if len(parts) != len(fields):
        raise ValueError(f"Cursor has {len(parts)} parts, expected {len(fields)}")

    return [_coerce_cursor_type(p) for p in parts]


def _coerce_cursor_type(value: str) -> Any:
    """Преобразует строковое значение курсора в подходящий тип."""
    try:
        return int(value)
    except (ValueError, TypeError):
        # Для str, UUID, datetime (ISO) оставляем как есть
        # SQLAlchemy сравнит строки лексикографически
        return value


def _apply_cursor_filter(stmt: Select, model: Type[DeclarativeBase],
                         fields: List[str], values: List[Any]) -> Select:
    """
    Применяет курсорную фильтрацию к запросу.

    Для одного поля: WHERE field > value
    Для составного: (a, b) > (x, y) → a > x OR (a == x AND b > y)
    """
    if len(fields) == 1:
        # Простое сравнение
        return stmt.where(getattr(model, fields[0]) > values[0])

    # Составное лексикографическое сравнение
    # Строим условие рекурсивно: (f1, f2, f3) > (v1, v2, v3)
    condition = None

    # Идём с конца к началу, строя вложенные условия
    for i in reversed(range(len(fields))):
        field = getattr(model, fields[i])
        value = values[i]

        if i == len(fields) - 1:
            # Последнее поле: просто >
            condition = field > value
        else:
            # Промежуточное: (field > value) OR (field == value AND next_condition)
            condition = or_(
                field > value,
                and_(field == value, condition)  # noqa
            )

    return stmt.where(condition) if condition is not None else stmt
