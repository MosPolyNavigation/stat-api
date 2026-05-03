from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
from collections import OrderedDict

from fastapi import HTTPException, Request, status

from app.state import AppState


class RateLimiter:
    """
    Guard для ограничения частоты запросов на эндпоинтах /api/stat/*.
    
    Особенности:
    - Раздельный учёт по эндпоинтам (endpoint_key)
    - LRU-вытеснение при превышении лимита пользователей
    - Очистка устаревших записей вынесена в фоновый воркер
    
    Структура хранения:
        user_access = {
            user_id: {
                endpoint_key: datetime,
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
        id_fields: List[str] = None,
        state_attr: str = "user_access",
        error_detail: str = "Too many requests for this user",
        ttl_seconds: int = 3600,  # 1 час по умолчанию
        max_users: int = DEFAULT_MAX_USERS,
        enabled: bool = True,
    ):
        self.window_seconds = window_seconds
        self.endpoint_key = endpoint_key
        self.id_fields = id_fields or ["user_id"]
        self.state_attr = state_attr
        self.error_detail = error_detail
        self.ttl_seconds = ttl_seconds
        self.max_users = max_users
        self.enabled = enabled
    
    async def __call__(self, request: Request) -> None:
        """Основной метод проверки лимита — без очистки."""
        if not self.enabled:
            return
        
        state: AppState = request.app.state.app_state
        access_store = getattr(state, self.state_attr, None)
        
        if access_store is None:
            access_store = OrderedDict()
            setattr(state, self.state_attr, access_store)
        
        user_id = await self._extract_user_id(request)
        if user_id is None:
            return
        
        ep_key = self.endpoint_key or self._extract_endpoint_key(request)
        if ep_key is None:
            return
        
        now = datetime.now()
        
        # Инициализируем запись пользователя
        if user_id not in access_store:
            access_store[user_id] = {}
        
        user_endpoints = access_store[user_id]
        last_access = user_endpoints.get(ep_key)
        
        if last_access is not None:
            delta = (now - last_access).total_seconds()
            if delta < self.window_seconds:
                retry_after = max(1, int(self.window_seconds - delta) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_detail,
                    headers={"Retry-After": str(retry_after)},
                )
        
        self._update_access(access_store, user_id, ep_key, now)
    
    def _extract_endpoint_key(self, request: Request) -> Optional[str]:
        path = request.url.path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2 and parts[-2] == "stat":
            return f"stat_{parts[-1]}"
        return path.replace("/", "_").strip("_") or None
    
    async def _extract_user_id(self, request: Request) -> Optional[Union[str, int]]:
        try:
            body = await request.json()
        except Exception:
            return None
        for field in self.id_fields:
            value = body.get(field)
            if value is not None:
                return value
        return None
    
    def _update_access(
        self,
        access_store: OrderedDict,
        user_id: Union[str, int],
        endpoint_key: str,
        now: datetime,
    ) -> None:
        """Обновляет время доступа с LRU-вытеснением."""
        if user_id not in access_store:
            access_store[user_id] = {}
        
        user_data = access_store[user_id]
        user_data.pop(endpoint_key, None)
        user_data[endpoint_key] = now
        
        if len(access_store) > self.max_users:
            to_remove = len(access_store) - self.max_users
            for _ in range(to_remove):
                access_store.popitem(last=False)
    
    def cleanup_expired(
        self,
        access_store: OrderedDict,
        now: Optional[datetime] = None,
        ttl_seconds: Optional[int] = None,
    ) -> int:
        """
        Удаляет устаревшие записи и пустые пользовательские словари.
        
        Args:
            access_store: Словарь состояния
            now: Текущее время (по умолчанию — сейчас)
            ttl_seconds: TTL в секундах (по умолчанию — self.ttl_seconds)
        
        Returns:
            int: Количество удалённых записей
        """
        if now is None:
            now = datetime.now()
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds
        
        threshold = timedelta(seconds=ttl_seconds)
        removed_count = 0
        
        for user_id in list(access_store.keys()):
            user_data = access_store[user_id]
            
            expired_eps = [
                ep_key for ep_key, ts in user_data.items()
                if now - ts > threshold
            ]
            for ep_key in expired_eps:
                del user_data[ep_key]
                removed_count += 1
            
            if not user_data:
                del access_store[user_id]
        
        return removed_count
    
    def cleanup_now(self, state: AppState) -> int:
        """Публичный метод для ручной очистки (используется воркером)."""
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            return 0
        return self.cleanup_expired(access_store)


stat_rate_limiter = RateLimiter(
    window_seconds=1.0,
    id_fields=["user_id"],
    error_detail="Too many requests for this user within one second",
    ttl_seconds=3600,
    max_users=1000,
)