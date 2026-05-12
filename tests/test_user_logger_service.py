import asyncio
import os
from unittest.mock import AsyncMock, MagicMock

from app.models import User, UserLog
from app.services.user_logger_service import UserLoggerService, background_log


class TestUserLoggerService:
    def test_00_log_returns_none_when_disabled(self):
        old_value = os.environ.get("STATAPI_LOGGING")
        os.environ["STATAPI_LOGGING"] = "0"
        try:
            service = UserLoggerService()
            user = User(id=1, login="admin", hash="x")
            result = service.log(user, "test")
            assert result is None
        finally:
            if old_value is None:
                os.environ.pop("STATAPI_LOGGING", None)
            else:
                os.environ["STATAPI_LOGGING"] = old_value

    def test_00_log_returns_none_when_user_is_none(self):
        service = UserLoggerService()
        result = service.log(None, "test")
        assert result is None

    def test_00_background_log_commits_record(self):
        async def run_test():
            session = AsyncMock()
            session.add = MagicMock()
            record = UserLog(user_id=1, text="test")

            await background_log(session, record)

            session.add.assert_called_once_with(record)
            session.commit.assert_awaited_once()
            session.rollback.assert_not_called()

        asyncio.run(run_test())

    def test_00_background_log_rolls_back_on_error(self):
        async def run_test():
            session = AsyncMock()
            session.add = MagicMock()
            session.commit.side_effect = Exception("db error")
            record = UserLog(user_id=1, text="test")

            await background_log(session, record)

            session.add.assert_called_once_with(record)
            session.commit.assert_awaited_once()
            session.rollback.assert_awaited_once()

        asyncio.run(run_test())
