from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status
from pydantic import ValidationError

from app.schemas import EventCreateRequest
from app.state import AppState


class RateLimiter:
    """
    Guard for rate-limiting writes to /api/stat/*.

    The current statistics API writes events through one endpoint, so the
    limiter stores access by user_id and event_key instead of by endpoint path.

    Storage:
        user_access = {
            user_id: {
                event_key: datetime,
                ...
            },
            ...
        }
    """

    DEFAULT_MAX_USERS: int = 10_000

    def __init__(
        self,
        window_seconds: float = 1.0,
        state_attr: str = "user_access",
        error_detail: str = "Too many requests for this user",
        ttl_seconds: int = 3600,
        max_users: int = DEFAULT_MAX_USERS,
        enabled: bool = True,
    ):
        self.window_seconds = window_seconds
        self.state_attr = state_attr
        self.error_detail = error_detail
        self.ttl_seconds = ttl_seconds
        self.max_users = max_users
        self.enabled = enabled

    async def __call__(self, request: Request) -> None:
        if not self.enabled:
            return

        data = await self._extract_event_request(request)
        if data is None:
            return

        state: AppState = request.app.state
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            access_store = OrderedDict()
            setattr(state, self.state_attr, access_store)

        now = datetime.now()
        ident = data.ident
        event_key = str(data.event_type_id)

        if ident not in access_store:
            access_store[ident] = {}

        user_events = access_store[ident]
        last_access = user_events.get(event_key)
        if last_access is not None:
            delta = (now - last_access).total_seconds()
            if delta < self.window_seconds:
                retry_after = max(1, int(self.window_seconds - delta) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=self.error_detail,
                    headers={"Retry-After": str(retry_after)},
                )

        self._update_access(access_store, ident, event_key, now)

    async def _extract_event_request(
        self,
        request: Request,
    ) -> Optional[EventCreateRequest]:
        try:
            body = await request.json()
            return EventCreateRequest.model_validate(body)
        except (ValueError, ValidationError):
            return None

    def _update_access(
        self,
        access_store: OrderedDict,
        user_id: str,
        event_key: str,
        now: datetime,
    ) -> None:
        if user_id not in access_store:
            access_store[user_id] = {}

        user_data = access_store[user_id]
        user_data.pop(event_key, None)
        user_data[event_key] = now
        access_store.move_to_end(user_id)

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
        if now is None:
            now = datetime.now()
        if ttl_seconds is None:
            ttl_seconds = self.ttl_seconds

        threshold = timedelta(seconds=ttl_seconds)
        removed_count = 0

        for user_id in list(access_store.keys()):
            user_data = access_store[user_id]
            expired_events = [
                event_key for event_key, ts in user_data.items()
                if now - ts > threshold
            ]
            for event_key in expired_events:
                del user_data[event_key]
                removed_count += 1

            if not user_data:
                del access_store[user_id]

        return removed_count

    def cleanup_now(self, state: AppState) -> int:
        access_store = getattr(state, self.state_attr, None)
        if access_store is None:
            return 0
        return self.cleanup_expired(access_store)


stat_rate_limiter = RateLimiter(
    window_seconds=1.0,
    error_detail="Too many requests for this event type within one second",
    ttl_seconds=3600,
    max_users=1000,
)
