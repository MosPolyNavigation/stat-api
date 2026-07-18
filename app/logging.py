import logging
import os
import sys


class ColorFormatter(logging.Formatter):
    """
    Форматтер с цветами:
    - Уровень и двоеточие слитно: INFO:
    - Цвет ТОЛЬКО у уровня, двоеточие и паддинги — без цвета
    - Вертикальное выравнивание за счёт паддинга ПОСЛЕ двоеточия
    """

    LEVEL_COLORS = {
        "DEBUG": "\x1b[36m",  # cyan
        "INFO": "\x1b[32m",  # green
        "WARNING": "\x1b[33m",  # yellow
        "ERROR": "\x1b[31m",  # red
        "CRITICAL": "\x1b[35m",  # magenta
    }
    RESET = "\x1b[0m"
    MAX_LEVEL_WIDTH = 9

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and (
            sys.stdout.isatty() or os.getenv("FORCE_COLOR") == "1"
        )
        # Форматтер для «хвоста»: имя логгера + сообщение
        self._rest_formatter = logging.Formatter("%(name)-22s | %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname

        # 1. Форматируем «хвост» (имя логгера + сообщение)
        rest = self._rest_formatter.format(record)

        # 2. Собираем уровень: цветное слово + нецветное двоеточие
        if self.use_colors and levelname in self.LEVEL_COLORS:
            colored_level = f"{self.LEVEL_COLORS[levelname]}{levelname}{self.RESET}"
        else:
            colored_level = levelname

        level_part = f"{colored_level}:"

        # 3. Паддинг ПОСЛЕ двоеточия — считаем по ЧИСТОЙ длине
        plain_width = len(levelname) + 1  # +1 за двоеточие
        padding = " " * (self.MAX_LEVEL_WIDTH - plain_width)

        # 4. Склеиваем
        return f"{level_part}{padding} | {rest}"


def setup_logging(level: str = "INFO", use_colors: bool = True) -> None:
    """
    Настраивает логирование для всего приложения.
    Вызывай ДО init_database() и создания FastAPI-приложения.
    """
    formatter = ColorFormatter(use_colors=use_colors)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, level.upper()))

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))

    if root.handlers:
        root.handlers.clear()

    root.addHandler(handler)

    # ── Настройка конкретных логгеров ──────────────────────────────────
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("app").setLevel(
        logging.DEBUG if level == "DEBUG" else logging.INFO
    )
