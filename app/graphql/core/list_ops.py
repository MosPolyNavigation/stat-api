from typing import TypeVar, List, Optional, Callable, Type, Any

from .filters import BaseFilterInput, filter_list
from .ordering import BaseOrderByInput, sort_list
from .pagination import PaginationInput, Connection, paginate_list

M = TypeVar("M")
T = TypeVar("T")


def process_list(
    models: List[M],
    model_type: Type,
    filters: Optional[BaseFilterInput] = None,
    order_by: Optional[BaseOrderByInput] = None,
    pagination: Optional[PaginationInput] = None,
    convert: Callable[[M], T] = lambda x: x,
) -> Connection[T]:
    """
    Применяет фильтрацию → сортировку → пагинацию к списку моделей.
    Порядок важен: сначала фильтруем, потом сортируем, потом пагинируем.
    """
    filtered = filter_list(models, model_type, filters)
    sorted_models = sort_list(filtered, order_by)
    return paginate_list(sorted_models, pagination, convert)
