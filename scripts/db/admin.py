import asyncio
from typing import Annotated

import typer
from pwdlib import PasswordHash
from sqlalchemy import select

from app.config import load_settings
from app.database import init_database, get_session_maker, close_database
from app.models.auth.user import User
from app.models.auth.user_role import UserRole


async def _create_or_update_admin(session_maker, login: str, hashed_pw: str) -> None:
    """Внутренняя async-логика: создание/обновление пользователя и привязка роли."""
    async with session_maker() as db:
        stmt = select(User).where(User.login == login)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.hash = hashed_pw
            typer.echo(f"🔄 Пользователь '{login}' найден. Пароль обновлён.")
        else:
            user = User()
            user.login = login
            user.hash = hashed_pw
            user.is_active = True
            db.add(user)
            typer.echo(f"🆕 Создаю пользователя '{login}'...")

        await db.flush()

        role_stmt = select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == 1
        )
        role_res = await db.execute(role_stmt)
        existing_role = role_res.scalar_one_or_none()

        if not existing_role:
            user_role = UserRole()
            user_role.user_id = user.id
            user_role.role_id = 1
            db.add(user_role)
            typer.echo("✅ Роль администратора назначена.")
        else:
            typer.echo("ℹ️ Роль администратора уже назначена.")

        await db.commit()


# ── Typer-команда (без декоратора) ───────────────────────────────────────
def create_admin_command(
    login: Annotated[str, typer.Argument(help="Логин администратора")],
) -> None:
    """
    Создание пользователя или обновление его пароля до администратора.
    Пароль запрашивается интерактивно (не сохраняется в истории терминала).
    Строка подключения берётся из конфига (переменная STATAPI_CONFIG).
    """
    # 🛡️ Интерактивный запрос пароля. Не попадает в history/bash/zsh/CI-логи
    try:
        password = typer.prompt(
            "Пароль администратора",
            hide_input=True,
            confirmation_prompt="Введите повторно для подтверждения",
        )
    except (EOFError, KeyboardInterrupt):
        typer.echo("\n⚠️ Ввод прерван.")
        raise typer.Exit(1)

    settings = load_settings()
    init_database(settings)
    session_maker = get_session_maker()

    password_hash = PasswordHash.recommended()
    hashed_pw = password_hash.hash(password)

    async def _run():
        await _create_or_update_admin(session_maker, login, hashed_pw)
        await close_database()

    try:
        asyncio.run(_run())
        typer.echo("✅ Операция завершена успешно.")
    except Exception as e:
        typer.echo(f"💥 Ошибка: {e}")
        raise typer.Exit(1)
