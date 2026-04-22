import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status

from app.state import AppState

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Guard для ограничения частоты запросов на эндпоинтах /api/stat/*.

    Особенности:
    - может использовать составной ключ доступа (например, client_id:event_type_id);
    - хранит последнее время запроса отдельно по ключу доступа и endpoint_key;
    - поддерживает LRU-вытеснение при превышении лимита хранимых ключей;
    - очистка устаревших записей выполняется фоновым воркером через cleanup_now.

    Структура хранения:
        access_store = {
            access_key: {
                endpoint_key: datetime,  # время последнего запроса
                ...
            },
            ...
        }
    """

    DEFAULT_MAX_USERS: int = 10_000

    def __init__(
        self,
        window_seconds: float = 1.0,
        endpoint_key: Optional[str] = None,
        id_fields: Optional[list[str]] = None,
        state_attr: str = "user_access",
        error_detail: str = "Too many requests for this user",
        ttl_seconds: int = 3600,
        max_users: Optional[int] = None,
        max_keys: Optional[int] = None,
        enabled: bool = True,
    ):
        self.window_seconds = window_seconds
        self.endpoint_key = endpoint_key
        self.id_fields = id_fields or ["user_id"]
        self.state_attr = state_attr
        self.error_detail = error_detail
        self.ttl_seconds = ttl_seconds
        self.max_keys = max_keys or max_users or self.DEFAULT_MAX_USERS
        self.enabled = enabled

    async def __call__(self, request: Request) -> None:
        """
        Основной метод проверки лимита.

        Если ключ лимитирования не удалось извлечь, ограничение пропускается.
        Это безопасно, так как дальнейшая бизнес-валидация запроса выполнится на эндпоинте.
        """
        if not self.enabled:
            return

        state: AppState = request.app.state
        access_store = getattr(state, self.state_attr, None)

        if access_store is None:
            access_store = OrderedDict()
            setattr(state, self.state_attr, access_store)

        access_key = await self._extract_rate_limit_key(request)
        if access_key is None:
            return

        ep_key = self.endpoint_key or self._extract_endpoint_key(request)
        if ep_key is None:
            return

        now = datetime.now()

        if access_key not in access_store:
            access_store[access_key] = {}

        endpoint_access = access_store[access_key]
        last_access = endpoint_access.get(ep_key)

        if last_access is not None:
            delta = (now - last_access).total_seconds()
            if delta < self.window_seconds:
                retry_after = max(1, int(self.window_seconds - delta) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_detail,
                    headers={"Retry-After": str(retry_after)},
                )

        self._update_access(access_store, access_key, ep_key, now)

    def _extract_endpoint_key(self, request: Request) -> Optional[str]:
        path = request.url.path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[-2] == "stat":
            return f"stat_{parts[-1]}"
        return path.replace("/", "_").strip("_") or None

    async def _extract_rate_limit_key(self, request: Request) -> Optional[str]:
        """
        Извлекает составной ключ лимитирования в формате "<client_id>:<event_type_id>".

        Источники client_id/client_ident:
        - request.state (если уже положен на предыдущем слое);
        - JSON-тело запроса;
        - служебные заголовки X-Client-Id / X-Client-Ident.

        Если одно из значений отсутствует, возвращает None и лимитер не блокирует запрос.
        """
        try:
            body = await request.json()
        except Exception:
            body = {}

        client_id = (
            getattr(request.state, "client_id", None)
            or getattr(request.state, "client_ident", None)
            or body.get("client_id")
            or body.get("client_ident")
            or body.get("ident")
            or request.headers.get("X-Client-Id")
            or request.headers.get("X-Client-Ident")
        )
        event_type_id = body.get("event_type_id")

        if client_id is None or event_type_id is None:
            return None

        rate_key = f"{client_id}:{event_type_id}"
        logger.debug("Rate limit key: %s", rate_key)
        return rate_key

    def _update_access(
        self,
        access_store: OrderedDict,
        access_key: str,
        endpoint_key: str,
        now: datetime,
    ) -> None:
        """
        Обновляет время доступа и применяет LRU-вытеснение при переполнении.

        Логика хранения:
        - по access_key храним словарь endpoint_key -> datetime;
        - при повторном обновлении endpoint_key сначала удаляем старое значение,
          затем вставляем новое, чтобы сохранить предсказуемый порядок в словаре.
        """
        if access_key not in access_store:
            access_store[access_key] = {}

        access_data = access_store[access_key]
        access_data.pop(endpoint_key, None)
        access_data[endpoint_key] = now

        if len(access_store) > self.max_keys:
            to_remove = len(access_store) - self.max_keys
            for _ in range(to_remove):
                access_store.popitem(last=False)

    def cleanup_expired(
        self,
        access_store: OrderedDict,
        now: Optional[datetime] = None,
        ttl_seconds: Optional[int] = None,
    ) -> int:
        """
        Удаляет устаревшие записи и пустые словари по ключам доступа.

        Args:
            access_store: текущее in-memory хранилище лимитера.
            now: текущее время (если не передано, берётся datetime.now()).
            ttl_seconds: TTL в секундах (если не передано, берётся self.ttl_seconds).

        Returns:
            int: количество удалённых endpoint-записей.
        """
        if now is None:
            now = datetime.now()
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds

        threshold = timedelta(seconds=ttl_seconds)
        removed_count = 0

        for access_key in list(access_store.keys()):
            access_data = access_store[access_key]

            expired_eps = [
                ep_key for ep_key, ts in access_data.items()
                if now - ts > threshold
            ]
            for ep_key in expired_eps:
                del access_data[ep_key]
                removed_count += 1

            if not access_data:
                del access_store[access_key]

        return removed_count

    def cleanup_now(self, state: AppState) -> int:
        """
        Публичный метод для ручной/фоновой очистки (используется cleanup-воркером).
        """
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            return 0
        return self.cleanup_expired(access_store)


stat_rate_limiter = RateLimiter(
    window_seconds=1.0,
    endpoint_key="stat_event",
    id_fields=["client_id", "event_type_id"],
    error_detail="Too many requests for this event type within one second",
    ttl_seconds=3600,
    max_keys=1000,
)
