import asyncio
from typing import Annotated

import typer

from app.config import load_settings
from app.database import init_database, close_database
from app.default_hooks import DefaultHooks
from app.helpers.seeder import apply_seeding, apply_seeding_isolated, rollback_seeding, rollback_seeding_isolated


def _filter_seeders(all_seeders, include: list[str] | None, exclude: list[str] | None) -> list:
    """Фильтрация сидеров по имени модели."""
    if not include and not exclude:
        return all_seeders

    filtered = []
    for seeder in all_seeders:
        name = seeder.model.__name__
        if include and name not in include:
            continue
        if exclude and name in exclude:
            continue
        filtered.append(seeder)
    return filtered


async def _run_seeding(
    seeders: list,
    isolated: bool,
    rollback: bool,
    dry_run: bool,
) -> None:
    """Внутренняя логика: применение или откат сидеров."""
    if dry_run:
        action = "🔄 Откат" if rollback else "🌱 Применение"
        mode = " (isolated)" if isolated else ""
        typer.echo(f"{action} сидеров{mode} [DRY RUN]:")
        for s in seeders:
            typer.echo(f"  • {s.model.__name__}")
        return

    if rollback:
        if isolated:
            await rollback_seeding_isolated(seeders)
        else:
            await rollback_seeding(seeders)
    else:
        if isolated:
            await apply_seeding_isolated(seeders)
        else:
            await apply_seeding(seeders)


# ── Функция без декоратора — чистая бизнес-логика ───────────────────────
def seed_command(
    isolated: Annotated[
        bool,
        typer.Option("--isolated", help="Запускать каждый сидер в отдельной транзакции"),
    ] = False,
    rollback: Annotated[
        bool,
        typer.Option("--rollback", help="Откатить данные, добавленные сидерами"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Показать план без выполнения"),
    ] = False,
    only: Annotated[
        list[str] | None,
        typer.Option("--only", help="Запустить только указанные сидеры (по имени модели)"),
    ] = None,
    skip: Annotated[
        list[str] | None,
        typer.Option("--skip", help="Пропустить указанные сидеры (по имени модели)"),
    ] = None,
) -> None:
    """
    Заполнение БД тестовыми/референсными данными.
    Строка подключения берётся из конфига (переменная STATAPI_CONFIG).
    """
    # Загружаем конфиг и получаем DSN
    settings = load_settings()

    typer.echo(f"🔄 Режим: {'откат' if rollback else 'применение'}")
    typer.echo(f"🧪 Isolated: {isolated}, Dry run: {dry_run}")

    # Инициализация БД
    init_database(settings)

    try:
        # Получаем все сидеры из хуков
        all_seeders = DefaultHooks().setup_seeders()
        typer.echo(f"📦 Всего сидеров: {len(all_seeders)}")

        # Фильтрация
        seeders = _filter_seeders(all_seeders, include=only, exclude=skip)
        if not seeders:
            typer.echo("⚠️ Нет сидеров для выполнения (проверьте --only / --skip)")
            return

        typer.echo(f"✅ Будет выполнено: {len(seeders)}")

        # Запуск
        asyncio.run(_run_seeding(seeders, isolated=isolated, rollback=rollback, dry_run=dry_run))

        if not dry_run:
            action = "🗑️ Откачено" if rollback else "🌱 Заполнено"
            typer.echo(f"{action} {len(seeders)} таблиц")

    except Exception as e:
        typer.echo(f"💥 Ошибка: {e}")
        raise typer.Exit(1)
    finally:
        # Гарантированная очистка ресурсов
        asyncio.run(close_database())
