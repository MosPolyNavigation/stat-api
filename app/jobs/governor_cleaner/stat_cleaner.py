import logging
from typing import List, Union

from fastapi import FastAPI

from app.state import AppState
from app.guards.governor import RateLimiter
from app.guards.review_governor import ReviewRateLimiter

logger = logging.getLogger(__name__)


def create_cleanup_job(
    app: FastAPI,
    limiters: List[Union[RateLimiter, ReviewRateLimiter]],
):
    """
    Создаёт функцию-джоб для очистки rate limiter state.
    Работает с обоими типами лимитеров.
    
    Логирует очистку с указанием класса лимитера.
    """
    def cleanup_job():
        try:
            state: AppState = app.state
            total_removed = 0
            
            for limiter in limiters:
                if not hasattr(limiter, 'cleanup_now'):
                    continue
                
                limiter_class = limiter.__class__.__name__
                
                removed = limiter.cleanup_now(state)
                total_removed += removed
                
                if removed > 0:
                    logger.info(
                        f"[{limiter_class}] Cleaned up {removed} expired entries"
                    )
            
            if total_removed > 0:
                logger.info(
                    f"[RateLimiterCleanup] Total removed: {total_removed} entries "
                    f"across {len(limiters)} limiter(s)"
                )
                
        except Exception as e:
            logger.error(
                f"[RateLimiterCleanup] Error during cleanup: {e}",
                exc_info=True
            )
    
    return cleanup_job