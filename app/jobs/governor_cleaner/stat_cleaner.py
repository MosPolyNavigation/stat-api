# app/workers/rate_limiter_cleanup.py
import logging
from typing import List

from fastapi import FastAPI

from app.state import AppState
from app.guards.governor import RateLimiter

logger = logging.getLogger(__name__)


def create_cleanup_job(
    app: FastAPI,
    limiters: List[RateLimiter],
):
    """
    Создаёт функцию-джоб для очистки rate limiter state.
    
    Returns:
        Callable: Функция без аргументов для передачи в scheduler.add_job()
    """
    def cleanup_job():
        try:
            state: AppState = app.state
            total_removed = 0
            
            for limiter in limiters:
                removed = limiter.cleanup_now(state)
                total_removed += removed
            
            if total_removed > 0:
                logger.info(f"[RateLimiterCleanup] Removed {total_removed} expired entries")
                
        except Exception as e:
            logger.error(f"[RateLimiterCleanup] Error: {e}", exc_info=True)
            # Не пробрасываем исключение, чтобы не ломать scheduler
    
    return cleanup_job