import typer
from scripts import CONFIG_ENV_NOTE
from scripts.db.seed.run import seed_command
from scripts.db.seed.nav_csv import nav_csv_command

seed_cli = typer.Typer(
    name="seed",
    help=f"🌱 Заполнение БД референсными данными.{CONFIG_ENV_NOTE}",
    add_completion=False,
    no_args_is_help=True,
)

# Регистрация команды через прямое применение декоратора
seed_cli.command(name="run", help="Запуск сидеров")(seed_command)

seed_cli.command(
    name="nav-csv", help="🗺️ Загрузка навигации из CSV"
)(nav_csv_command)
