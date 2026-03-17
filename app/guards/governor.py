# app/guards/rate_limiter.py
from datetime import datetime, timedelta
from typing import Optional, Union, List
from collections import OrderedDict

from fastapi import HTTPException, Request, status

from app.state import AppState


class RateLimiter:
    """
    Guard для ограничения частоты запросов на эндпоинтах /api/stat/*.
    
    Особенности:
    - Автоматическая очистка устаревших записей (TTL)
    - LRU-вытеснение при превышении лимита пользователей
    - Поддержка разных полей ID (user_id, tg_id, etc.)
    
    НЕ применяется к /api/stat/tg-bot (там токенная авторизация)
    """
    
    DEFAULT_TTL_HOURS: int = 1
    DEFAULT_MAX_USERS: int = 10_000
    CLEANUP_INTERVAL: int = 100
    
    def __init__(
        self,
        window_seconds: float = 1.0,
        id_fields: List[str] = None,
        state_attr: str = "user_access",
        error_detail: str = "Too many requests for this user",
        ttl_hours: int = DEFAULT_TTL_HOURS,
        max_users: int = DEFAULT_MAX_USERS,
        enabled: bool = True,
    ):
        self.window_seconds = window_seconds
        self.id_fields = id_fields or ["user_id"]
        self.state_attr = state_attr
        self.error_detail = error_detail
        self.ttl_seconds = ttl_hours * 3600
        self.max_users = max_users
        self.enabled = enabled
        self._request_counter = 0
    
    async def __call__(self, request: Request) -> None:
        if not self.enabled:
            return
        
        state: AppState = request.app.state
        access_store = getattr(state, self.state_attr, None)
        
        if access_store is None:
            access_store = OrderedDict()
            setattr(state, self.state_attr, access_store)
        
        user_id = await self._extract_user_id(request)
        if user_id is None:
            return
        
        now = datetime.now()
        
        # Периодическая очистка
        self._request_counter += 1
        if self._request_counter >= self.CLEANUP_INTERVAL:
            self._cleanup_expired(access_store, now)
            self._request_counter = 0
        
        last_access = access_store.get(user_id)
        
        if last_access is not None:
            delta = (now - last_access).total_seconds()
            if delta < self.window_seconds:
                retry_after = max(1, int(self.window_seconds - delta) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_detail,
                    headers={"Retry-After": str(retry_after)},
                )
        
        self._update_access(access_store, user_id, now)
    
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
        now: datetime,
    ) -> None:
        access_store.pop(user_id, None)
        access_store[user_id] = now
        
        if len(access_store) > self.max_users:
            to_remove = len(access_store) - self.max_users
            for _ in range(to_remove):
                access_store.popitem(last=False)
    
    def _cleanup_expired(
        self,
        access_store: OrderedDict,
        now: datetime,
        threshold: Optional[timedelta] = None,
    ) -> int:
        if threshold is None:
            threshold = timedelta(seconds=self.ttl_seconds)
        
        expired_keys = [
            key for key, ts in list(access_store.items())
            if now - ts > threshold
        ]
        
        for key in expired_keys:
            del access_store[key]
        
        return len(expired_keys)
    
    def cleanup_now(self, state: AppState) -> int:
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            return 0
        return self._cleanup_expired(access_store, datetime.now())


stat_rate_limiter = RateLimiter(
    window_seconds=1.0,
    id_fields=["user_id"],
    error_detail="Too many requests for this user within one second",
    ttl_hours=1,
    max_users=10_000,
)