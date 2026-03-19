import strawberry
from typing import Optional


@strawberry.type
class PageInfo:
    """Информация о навигации по страницам."""
    has_previous_page: bool
    has_next_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@strawberry.type
class PaginationInfo:
    """Дополнительная информация о пагинации."""
    total_count: int
    current_page: int
    total_pages: int


@strawberry.input
class PaginationInput:
    """Входные параметры для пагинации."""
    limit: Optional[int] = 10
    offset: Optional[int] = 0


@strawberry.input
class OffsetInput:
    """Параметр смещения."""
    offset: Optional[int] = 0


@strawberry.input
class CursorInput:
    """Параметр курсора."""
    cursor: Optional[str] = None
