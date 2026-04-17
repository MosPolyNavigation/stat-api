import asyncio
import logging

from sqlalchemy.exc import SQLAlchemyError
from app.database import AsyncSessionLocal
from app.services.refresh_token_service import RefreshTokenService

logger = logging.getLogger(f"uvicorn.{__name__}")

# отзывает все refresh-токены, срок действия которых уже истёк
async def revoke_expired_refresh_tokens() -> None:
    try:
        async with AsyncSessionLocal() as db:
            service = RefreshTokenService(db)
            revoked_count = await service.revoke_expired_tokens()
            await db.commit()

        logger.info(
            "[RefreshTokenCleanup] Expired refresh tokens revoked: %s",
            revoked_count,
        )
    except asyncio.CancelledError:
        logger.info("[RefreshTokenCleanup] Revoke job cancelled gracefully")
        raise
    except SQLAlchemyError:
        logger.exception("[RefreshTokenCleanup] Database error during expired token revoke")
    except Exception:
        logger.exception("[RefreshTokenCleanup] Unexpected error during expired token revoke")


# Удаляет refresh-токены, срок действия которых истек более 30 дней назад
async def delete_old_refresh_tokens() -> None:
    try:
        async with AsyncSessionLocal() as db:
            service = RefreshTokenService(db)
            deleted_count = await service.delete_expired_tokens()
            await db.commit()

        logger.info(
            "[RefreshTokenCleanup] Old refresh tokens deleted: %s",
            deleted_count,
        )
    except asyncio.CancelledError:
        logger.info("[RefreshTokenCleanup] Delete job cancelled gracefully")
        raise
    except SQLAlchemyError:
        logger.exception("[RefreshTokenCleanup] Database error during old token delete")
    except Exception:
        logger.exception("[RefreshTokenCleanup] Unexpected error during old token delete")
