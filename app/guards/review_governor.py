from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict
from collections import OrderedDict

from fastapi import HTTPException, Request, status

from app.state import AppState


class ReviewRateLimiter:
    """
    Guard для ограничения частоты отправки отзывов.
    
    Правила:
    - Не более 5 запросов в минуту
    - Не более 20 запросов за 5 минут
    - Перманентный бан при значительном превышении лимитов
    
    Структура хранения:
        user_review_access = {
            user_id: {
                "requests": [datetime, datetime, ...],  # timestamps запросов
                "banned": bool,                          # флаг бана
                "ban_reason": str | None,                # причина бана
                "ban_timestamp": datetime | None,        # когда забанен
                "violation_count": int,                  # количество нарушений
            }
        }
    """
    
    # Лимиты
    WINDOW_1_MIN_MAX: int = 5
    WINDOW_5_MIN_MAX: int = 20
    
    # Порог для перманентного бана
    BAN_THRESHOLD_VIOLATIONS: int = 25  # после 10 нарушений
    BAN_THRESHOLD_BURST: int = 20       # или 20+ запросов за 10 секунд
    
    # TTL для небанальных пользователей (часы)
    DEFAULT_TTL_HOURS: int = 24
    # Максимум пользователей в памяти
    DEFAULT_MAX_USERS: int = 10_000
    
    def __init__(
        self,
        state_attr: str = "user_review_access",
        ttl_hours: int = DEFAULT_TTL_HOURS,
        max_users: int = DEFAULT_MAX_USERS,
        enabled: bool = True,
    ):
        self.state_attr = state_attr
        self.ttl_seconds = ttl_hours * 3600
        self.max_users = max_users
        self.enabled = enabled
    
    async def __call__(self, request: Request) -> None:
        """Основной метод проверки лимитов."""
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
        
        if user_id not in access_store:
            access_store[user_id] = {
                "requests": [],
                "banned": False,
                "ban_reason": None,
                "ban_timestamp": None,
                "violation_count": 0,
            }
        
        user_data = access_store[user_id]
        
        # Проверка на бан
        if user_data["banned"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User permanently banned: {user_data['ban_reason']}",
                headers={"X-Ban-Reason": user_data["ban_reason"] or "unknown"},
            )
        
        # Очищаем старые запросы (старше 5 минут)
        self._cleanup_old_requests(user_data, now)
        
        user_data["requests"].append(now)
        
        requests = user_data["requests"]

        # Проверка на burst-атаку (30+ запросов за 10 секунд)
        ten_sec_ago = now - timedelta(seconds=10)
        requests_10sec = [ts for ts in requests if ts > ten_sec_ago]
        
        if len(requests_10sec) >= self.BAN_THRESHOLD_BURST:
            user_data["banned"] = True
            user_data["ban_reason"] = "Burst attack detected"
            user_data["ban_timestamp"] = now
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User permanently banned: Burst attack detected",
                headers={"X-Ban-Reason": "Burst attack detected"},
            )
        
        # Проверка: 5 запросов в минуту
        one_min_ago = now - timedelta(minutes=1)
        requests_1min = [ts for ts in requests if ts > one_min_ago]
        
        if len(requests_1min) > self.WINDOW_1_MIN_MAX:
            user_data["violation_count"] += 1
            self._check_and_ban(user_data, now)
            
            if user_data["banned"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User banned for excessive violations: {user_data['ban_reason']}",
                )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many reviews. Max {self.WINDOW_1_MIN_MAX} per minute.",
                headers={"Retry-After": "60"},
            )
        
        # Проверка: 20 запросов за 5 минут
        five_min_ago = now - timedelta(minutes=5)
        requests_5min = [ts for ts in requests if ts > five_min_ago]
        
        if len(requests_5min) >= self.WINDOW_5_MIN_MAX:
            user_data["violation_count"] += 1
            self._check_and_ban(user_data, now)
            
            if user_data["banned"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User banned for excessive violations: {user_data['ban_reason']}",
                )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many reviews. Max {self.WINDOW_5_MIN_MAX} per 5 minutes.",
                headers={"Retry-After": "300"},
            )
        
        # LRU-вытеснение при превышении лимита пользователей
        self._enforce_max_users(access_store)
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Извлекает user_id из multipart/form-data или JSON."""
        try:
            content_type = request.headers.get("content-type", "")
            
            if "multipart/form-data" in content_type:
                form = await request.form()
                return form.get("user_id")
            else:
                body = await request.json()
                return body.get("user_id")
        except Exception:
            return None
    
    def _cleanup_old_requests(
        self,
        user_data: Dict,
        now: datetime,
    ) -> None:
        """Удаляет запросы старше 5 минут."""
        five_min_ago = now - timedelta(minutes=5)
        user_data["requests"] = [
            ts for ts in user_data["requests"]
            if ts > five_min_ago
        ]
    
    def _check_and_ban(
        self,
        user_data: Dict,
        now: datetime,
    ) -> None:
        """Проверяет, нужно ли банить пользователя."""
        if user_data["violation_count"] >= self.BAN_THRESHOLD_VIOLATIONS:
            user_data["banned"] = True
            user_data["ban_reason"] = f"Excessive violations ({user_data['violation_count']} times)"
            user_data["ban_timestamp"] = now
    
    def _enforce_max_users(
        self,
        access_store: OrderedDict,
    ) -> None:
        """LRU-вытеснение старых пользователей."""
        if len(access_store) > self.max_users:
            to_remove = len(access_store) - self.max_users
            for _ in range(to_remove):
                access_store.popitem(last=False)
    
    def cleanup_expired(
        self,
        access_store: OrderedDict,
        now: Optional[datetime] = None,
    ) -> int:
        """
        Удаляет устаревшие записи (небанальных пользователей без активности).
        Забаненные пользователи хранятся отдельно.
        """
        if now is None:
            now = datetime.now()
        
        threshold = timedelta(seconds=self.ttl_seconds)
        removed_count = 0
        
        for user_id in list(access_store.keys()):
            user_data = access_store[user_id]
            
            # Забаненных не удаляем (или можно удалять через другой TTL)
            if user_data["banned"]:
                continue
            
            # Если нет запросов или все запросы старые — удаляем
            if not user_data["requests"]:
                del access_store[user_id]
                removed_count += 1
                continue
            
            last_request = max(user_data["requests"])
            if now - last_request > threshold:
                del access_store[user_id]
                removed_count += 1
        
        return removed_count
    
    def cleanup_now(self, state: AppState) -> int:
        """Публичный метод для ручной очистки (используется воркером)."""
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            return 0
        return self.cleanup_expired(access_store)
    
    def get_user_status(
        self,
        state: AppState,
        user_id: str,
    ) -> Dict:
        """
        Возвращает статус пользователя (для админки/мониторинга).
        """
        access_store = getattr(state, self.state_attr, None)
        if access_store is None or user_id not in access_store:
            return {"exists": False}
        
        user_data = access_store[user_id]
        now = datetime.now()
        
        # Считаем активные запросы
        requests_1min = [
            ts for ts in user_data["requests"]
            if ts > now - timedelta(minutes=1)
        ]
        requests_5min = [
            ts for ts in user_data["requests"]
            if ts > now - timedelta(minutes=5)
        ]
        
        return {
            "exists": True,
            "banned": user_data["banned"],
            "ban_reason": user_data["ban_reason"],
            "ban_timestamp": user_data["ban_timestamp"],
            "violation_count": user_data["violation_count"],
            "requests_1min": len(requests_1min),
            "requests_5min": len(requests_5min),
            "limit_1min": self.WINDOW_1_MIN_MAX,
            "limit_5min": self.WINDOW_5_MIN_MAX,
        }
    
    def unban_user(
        self,
        state: AppState,
        user_id: str,
    ) -> bool:
        """
        Снимает бан с пользователя (для админки).
        Returns True если успешно, False если пользователь не найден.
        """
        access_store = getattr(state, self.state_attr, None)
        if access_store is None or user_id not in access_store:
            return False
        
        user_data = access_store[user_id]
        user_data["banned"] = False
        user_data["ban_reason"] = None
        user_data["ban_timestamp"] = None
        user_data["violation_count"] = 0
        user_data["requests"] = []  # сбрасываем историю
        
        return True


review_rate_limiter = ReviewRateLimiter(
    ttl_hours=24,      # хранить активность 24 часа
    max_users=1000,  # максимум 10k пользователей
)