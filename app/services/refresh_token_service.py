from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import RefreshToken

# Сервис для работы с refresh-токенами
class RefreshTokenService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        """
        Возвращает refresh-токен по его jti или None, если токен не найден.
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token: RefreshToken) -> bool:
        """
        Помечает refresh-токен как отозванный.
        Возвращает False, если токен уже был отозван, иначе True.
        """
        if token.revoked:
            return False

        token.revoked = True
        return True

    async def revoke_expired_tokens(self) -> int:
        """
        Помечает все истекшие и ещё не отозванные refresh-токены как отозванные.
        Возвращает количество затронутых записей.
        """
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)

        result = await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.exp_date <= current_time)
            .where(RefreshToken.revoked.is_(False))
            .values(revoked=True)
        )

        affected_rows = result.rowcount
        if affected_rows is None:
            return 0
        return affected_rows

    async def delete_expired_tokens(self) -> int:
        """
        Удаляет refresh-токены, срок действия которых истек более 30 дней назад.
        Возвращает количество удалённых записей.
        """
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        delete_before = current_time - timedelta(days=30)

        result = await self.db.execute(
            delete(RefreshToken).where(RefreshToken.exp_date <= delete_before)
        )

        affected_rows = result.rowcount
        if affected_rows is None:
            return 0
        return affected_rows
