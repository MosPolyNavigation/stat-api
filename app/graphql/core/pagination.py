from typing import TypeVar, Generic, List, Optional, Callable, Any
import math
import strawberry
from sqlalchemy import func, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


def pagination_input_from_attrs(page: int = 1, page_size: int = 10):
    return PaginationInput(page=page, page_size=page_size)


# =============================================================================
# 1. GraphQL-типы
# =============================================================================
@strawberry.input
class PaginationInput:
    page: int = strawberry.field(default=1, description="Номер страницы (1-based)")
    page_size: int = strawberry.field(default=10, description="Количество элементов на странице")


@strawberry.type
class PageInfo:
    has_previous_page: bool
    has_next_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None


@strawberry.type
class PaginationInfo:
    total_count: int
    current_page: int
    total_pages: int


@strawberry.type
class Connection(Generic[T]):
    nodes: List[T]
    page_info: PageInfo
    pagination_info: PaginationInfo


# =============================================================================
# 2. Ядро пагинации
# =============================================================================
async def paginate_query(
        session: AsyncSession,
        stmt: Select,
        pagination: PaginationInput,
        convert: Callable[[Any], T] = lambda x: x,
) -> Connection[T]:
    page = max(1, pagination.page)
    page_size = max(1, min(200, pagination.page_size))
    offset = (page - 1) * page_size

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await session.execute(count_stmt)).scalar_one() or 0
    total_pages = max(1, math.ceil(total_count / page_size))

    paginated_stmt = stmt.offset(offset).limit(page_size)
    result = await session.execute(paginated_stmt)
    raw_items = result.scalars().all()
    nodes = [convert(item) for item in raw_items]

    return Connection(
        nodes=nodes,
        page_info=PageInfo(
            has_previous_page=page > 1,
            has_next_page=page < total_pages,
            start_cursor=str(offset) if raw_items else None,
            end_cursor=str(offset + len(raw_items) - 1) if raw_items else None,
        ),
        pagination_info=PaginationInfo(
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
        )
    )


def paginate_list(
        models: List[T],
        pagination: Optional[PaginationInput],
        convert: Callable[[Any], T] = lambda x: x,
) -> Connection[T]:
    """Пагинирует уже отфильтрованный и отсортированный список."""
    pagination = pagination or PaginationInput(page=1, page_size=10)
    page = max(1, pagination.page)
    page_size = max(1, min(200, pagination.page_size))

    total_count = len(models)
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    offset = (page - 1) * page_size
    paginated = models[offset:offset + page_size]
    nodes = [convert(m) for m in paginated]

    return Connection(
        nodes=nodes,
        page_info=PageInfo(
            has_previous_page=page > 1,
            has_next_page=page < total_pages,
            start_cursor=str(offset) if nodes else None,
            end_cursor=str(offset + len(nodes) - 1) if nodes else None,
        ),
        pagination_info=PaginationInfo(
            total_count=total_count,
            current_page=page,
            total_pages=total_pages,
        )
    )
