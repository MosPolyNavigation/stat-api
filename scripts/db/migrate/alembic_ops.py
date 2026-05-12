import subprocess
import sys
from typing import Annotated

import typer


def _run_alembic(command: str, args: list[str]) -> int:
    """Запуск alembic CLI через subprocess с пробросом stdout/stderr."""
    cmd = [sys.executable, "-m", "alembic", command] + args
    typer.echo(f"🔧 Запуск: {' '.join(cmd)}")
    try:
        # stdout/stderr наследуются по умолчанию, вывод alembic будет виден сразу
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        typer.echo(f"💥 Alembic завершился с ошибкой (код {e.returncode})")
        return e.returncode
    except FileNotFoundError:
        typer.echo("❌ Alembic не найден. Убедитесь, что пакет установлен в окружении.")
        return 1


def upgrade_command(
    revision: Annotated[str, typer.Argument(help="Целевая ревизия (по умолчанию head)")] = "head",
    sql: Annotated[bool, typer.Option("--sql", help="Вывести SQL-скрипт вместо выполнения")] = False,
    tag: Annotated[str | None, typer.Option("--tag", help="Тег для миграции")] = None,
) -> None:
    """Применение миграций Alembic. DSN берётся из конфига (STATAPI_CONFIG)."""
    args = [revision]
    if sql:
        args.append("--sql")
    if tag:
        args.extend(["--tag", tag])
    raise typer.Exit(_run_alembic("upgrade", args))


def downgrade_command(
    revision: Annotated[str, typer.Argument(help="Целевая ревизия (по умолчанию -1)")] = "-1",
    sql: Annotated[bool, typer.Option("--sql", help="Вывести SQL-скрипт вместо выполнения")] = False,
    tag: Annotated[str | None, typer.Option("--tag", help="Тег для миграции")] = None,
) -> None:
    """Откат миграций Alembic. DSN берётся из конфига (STATAPI_CONFIG)."""
    args = [revision]
    if sql:
        args.append("--sql")
    if tag:
        args.extend(["--tag", tag])
    raise typer.Exit(_run_alembic("downgrade", args))
