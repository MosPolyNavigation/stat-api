import typer
from scripts import CONFIG_ENV_NOTE
from scripts.db.migrate.sqlite_to_pg import sqlite_to_pg_command
from scripts.db.migrate.old_events_to_new import old_events_to_new_command
from scripts.db.migrate.alembic_ops import upgrade_command, downgrade_command

migrate_cli = typer.Typer(
    name="migrate",
    help=f"🔄 Кастомные скрипты миграции данных.{CONFIG_ENV_NOTE}",
    add_completion=False,
    no_args_is_help=True,
)

migrate_cli.command(
    name="sqlite-to-pg",
    help="🗄️ Перенос данных из SQLite в PostgreSQL"
)(sqlite_to_pg_command)

migrate_cli.command(  # ← новая команда
    name="old-events-to-new",
    help="🔄 Переход на новую систему событий"
)(old_events_to_new_command)

migrate_cli.command(  # ← новые команды
    name="upgrade",
    help="⬆️ Применить миграции Alembic"
)(upgrade_command)

migrate_cli.command(
    name="downgrade",
    help="⬇️ Откатить миграции Alembic"
)(downgrade_command)
