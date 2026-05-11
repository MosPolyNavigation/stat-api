import asyncio
import os
import time
import uuid

from pwdlib import PasswordHash
from sqlalchemy import select

from .base import client, session_maker as session_maker
from app.models import User, UserLog

password_hash = PasswordHash.recommended()


async def get_logs() -> list[UserLog]:
    async with session_maker() as db:
        result = await db.execute(select(UserLog).order_by(UserLog.id))
        return list(result.scalars().all())


def wait_for_log_count(expected_count: int, timeout: float = 1.0) -> list[UserLog]:
    started_at = time.time()

    while time.time() - started_at < timeout:
        logs = asyncio.run(get_logs())
        if len(logs) >= expected_count:
            return logs
        time.sleep(0.05)

    return asyncio.run(get_logs())


def graphql_query(query: str, headers: dict | None = None):
    return client.post(
        "/api/graphql",
        json={"query": query},
        headers=headers or {},
    )


def get_access_token(login: str, password: str) -> str:
    response = client.post(
        "/api/auth/token",
        data={
            "username": login,
            "password": password,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


async def ensure_guest_user() -> tuple[str, str]:
    login = f"guest_{uuid.uuid4().hex[:8]}"
    password = "guest_password"

    async with session_maker() as db:
        guest_user = User(
            login=login,
            hash=password_hash.hash(password),
        )
        db.add(guest_user)
        await db.commit()

    return login, password


class TestGraphQLLogging:
    def test_00_graphql_forbidden_error_is_masked_and_logged(self):
        old_value = os.environ.get("STATAPI_LOGGING")
        os.environ["STATAPI_LOGGING"] = "1"

        try:
            guest_login, guest_password = asyncio.run(ensure_guest_user())

            guest_token = get_access_token(guest_login, guest_password)
            headers = {"Authorization": f"Bearer {guest_token}"}

            before_logs = asyncio.run(get_logs())

            response = graphql_query(
                """
                mutation {
                    createUser(data: {
                        login: "forbidden_logger_user",
                        password: "password123",
                        isActive: true
                    }) {
                        id
                        login
                    }
                }
                """,
                headers,
            )

            assert response.status_code == 200, response.text

            payload = response.json()
            assert "errors" in payload
            assert payload["errors"][0]["message"] == "Недостаточно прав для выполнения операции"
            assert "extensions" not in payload["errors"][0]

            after_logs = wait_for_log_count(len(before_logs) + 1)
            assert len(after_logs) == len(before_logs) + 1
            assert "Попытка выполнить действие за рамками прав пользователя" in after_logs[-1].text

        finally:
            if old_value is None:
                os.environ.pop("STATAPI_LOGGING", None)
            else:
                os.environ["STATAPI_LOGGING"] = old_value