from typing import Optional, Tuple
from .pagination import PaginationInput, PageInfo, PaginationInfo


def _validated_limit_2(limit: Optional[int]) -> int:
    """Валидация лимита записей."""
    if limit is None:
        return 10
    if limit < 0:
        return 0
    MAX_LIMIT = 100
    return min(limit, MAX_LIMIT)


def _validated_offset(offset: Optional[int]) -> int:
    """Валидация оффсета."""
    if offset is None or offset < 0:
        return 0
    return offset


def _create_pagination_info(
    total_count: int,
    offset: int,
    limit: int,
    records_count: int
) -> Tuple[PageInfo, PaginationInfo]:
    """Создание объектов PageInfo и PaginationInfo."""
    
    has_previous_page = offset > 0
    has_next_page = offset + records_count < total_count
    
    start_cursor = str(offset) if records_count > 0 else None
    end_cursor = str(offset + records_count - 1) if records_count > 0 else None
    
    page_info = PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=start_cursor,
        end_cursor=end_cursor
    )
    
    validated_limit = max(limit, 1)
    total_pages = (total_count + validated_limit - 1) // validated_limit if validated_limit > 0 else 0
    current_page = (offset // validated_limit) + 1 if validated_limit > 0 else 1
    
    pagination_info = PaginationInfo(
        total_count=total_count,
        current_page=current_page,
        total_pages=total_pages
    )
    
    return page_info, pagination_info


def _validated_limit(limit: Optional[int]) -> Optional[int]:
    if limit is None:
        return None
    if limit <= 0:
        return 0
    return limit
