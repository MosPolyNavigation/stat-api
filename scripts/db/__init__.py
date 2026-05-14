import typer
from scripts import CONFIG_ENV_NOTE
from scripts.db.migrate import migrate_cli
from scripts.db.seed import seed_cli
from scripts.db.admin import create_admin_command

db_cli = typer.Typer(
    name="db",
    help=f"🗄️ Управление базой данных и миграциями.{CONFIG_ENV_NOTE}",
    add_completion=False,
    no_args_is_help=True,  # Покажет справку, если вызвать просто `stat-api db`
)

# Подключаем группу migrate к db
db_cli.add_typer(migrate_cli, name="migrate")
db_cli.add_typer(seed_cli, name="seed")

db_cli.command(name="create-admin", help="👤 Создание или обновление администратора")(
    create_admin_command
)
