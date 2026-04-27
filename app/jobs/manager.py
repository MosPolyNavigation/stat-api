import functools
import logging
import uuid
from datetime import datetime, timezone
from os import path
from typing import Any, Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import BackgroundTasks

from app.jobs.models.job_config import JobsConfig, JobConfig
from app.jobs.queue_db import (
    init_queue_db,
    log_job_start,
    log_job_success,
    log_job_error,
    get_job_history,
)

logger = logging.getLogger(__name__)

# ─── Приватный реестр задач (заполняется при импорте через @scheduled_task) ───

__TASK_REGISTRY: list[dict[str, Any]] = []

# Счётчик текущих запущенных инстансов: name -> количество
_RUNNING_TASKS: dict[str, int] = {}

# Путь к queue.db — устанавливается в JobManager.start()
_DB_PATH: str | None = None


# ─── Публичный API реестра ────────────────────────────────────────────────────

def get_task_registry() -> list[dict[str, Any]]:
    """Возвращает копию реестра для чтения."""
    return list(__TASK_REGISTRY)


def clear_task_registry() -> None:
    """⚠️ Только для тестов: очищает глобальный реестр и счётчики."""
    global __TASK_REGISTRY, _RUNNING_TASKS, _DB_PATH
    __TASK_REGISTRY.clear()
    _RUNNING_TASKS.clear()
    _DB_PATH = None


# ─── Декоратор @scheduled_task ────────────────────────────────────────────────

def scheduled_task(name: str, **overrides: Any) -> Callable:
    """
    Статический декоратор для регистрации async-функции в реестре задач.

    Оборачивает функцию: при каждом вызове генерирует run_id, пишет старт/финиш/ошибку
    в queue.db и защищает от параллельного запуска (по max_instances).

    Пример:
        @scheduled_task(name="fetch_location_data")
        async def fetch_location_data(): ...
    """
    def decorator(func: Callable[..., Awaitable]) -> Callable:
        @functools.wraps(func)
        async def wrapper(
            *args,
            _triggered_by: str = "scheduler",
            _run_id: str | None = None,
            **kwargs,
        ):
            # Берём max_instances из записи реестра (может быть обновлён setup_from_config)
            entry = next((t for t in get_task_registry() if t["name"] == name), None)
            max_instances: int = entry["max_instances"] if entry else 1

            current = _RUNNING_TASKS.get(name, 0)
            if current >= max_instances:
                logger.warning(
                    "Task '%s' already has %d/%d running instance(s), skipping",
                    name, current, max_instances,
                )
                return

            run_id = _run_id or str(uuid.uuid4())
            _RUNNING_TASKS[name] = current + 1
            started_at = datetime.now(timezone.utc)

            if _DB_PATH:
                try:
                    await log_job_start(_DB_PATH, name, run_id, _triggered_by)
                except Exception as e:
                    logger.error("Failed to log start for '%s': %s", name, e)

            try:
                result = await func(*args, **kwargs)
                if _DB_PATH:
                    try:
                        await log_job_success(_DB_PATH, run_id, started_at)
                    except Exception as e:
                        logger.error("Failed to log success for '%s': %s", name, e)
                return result
            except Exception as e:
                if _DB_PATH:
                    try:
                        await log_job_error(_DB_PATH, run_id, started_at, e)
                    except Exception as le:
                        logger.error("Failed to log error for '%s': %s", name, le)
                raise
            finally:
                _RUNNING_TASKS[name] = max(0, _RUNNING_TASKS.get(name, 1) - 1)

        # Регистрируем в реестре при импорте модуля
        __TASK_REGISTRY.append({
            "name": name,
            "func": wrapper,
            "original": func,
            "overrides": overrides,
            # max_instances может быть переопределён из конфига в setup_from_config
            "max_instances": overrides.get("max_instances", 1),
        })
        return wrapper

    return decorator


# ─── JobManager ──────────────────────────────────────────────────────────────

class JobManager:
    """
    Читает реестр __TASK_REGISTRY, настраивает APScheduler из конфига
    и предоставляет методы управления задачами для API.
    """

    def __init__(
        self,
        static_path: str,
        queue_type: str = "sqlite",
        queue_db: str = "queue.db",
    ):
        self._db_path = path.join(static_path, queue_db)
        self._scheduler: AsyncIOScheduler | None = None
        self._job_configs: dict[str, JobConfig] = {}

    @property
    def db_path(self) -> str:
        return self._db_path

    # ── Инициализация ─────────────────────────────────────────────────────────

    def setup_from_config(self, jobs_config: JobsConfig) -> None:
        """
        Создаёт планировщик и регистрирует в нём задачи из конфига.
        Задачи с enabled=false пропускаются.
        Задачи, которых нет в реестре (@scheduled_task), логируются как warning.
        """
        self._scheduler = AsyncIOScheduler({"apscheduler.timezone": "Europe/Moscow"})
        registry_by_name = {entry["name"]: entry for entry in get_task_registry()}

        for job_cfg in jobs_config.tasks:
            self._job_configs[job_cfg.name] = job_cfg

            # Обновляем max_instances в реестре из конфига
            if job_cfg.name in registry_by_name:
                registry_by_name[job_cfg.name]["max_instances"] = job_cfg.scheduler.max_instances

            if not job_cfg.enabled:
                logger.info("Job '%s' disabled in config, skipping", job_cfg.name)
                continue

            if job_cfg.name not in registry_by_name:
                logger.warning(
                    "Job '%s' is in config but not registered via @scheduled_task",
                    job_cfg.name,
                )
                continue

            func = registry_by_name[job_cfg.name]["func"]
            self._scheduler.add_job(func, **self._build_apscheduler_kwargs(job_cfg))
            logger.info("Scheduled job '%s' with trigger '%s'", job_cfg.name, job_cfg.trigger)

    def add_job(self, func: Callable, **kwargs) -> None:
        """Добавляет произвольную задачу в планировщик (для системных задач, не входящих в реестр)."""
        if self._scheduler is None:
            raise RuntimeError("setup_from_config() не был вызван")
        self._scheduler.add_job(func, **kwargs)

    async def start(self) -> None:
        """Инициализирует queue.db и запускает планировщик."""
        global _DB_PATH
        _DB_PATH = self._db_path
        await init_queue_db(self._db_path)
        if self._scheduler:
            self._scheduler.start()
            logger.info("JobManager started, queue db: %s", self._db_path)

    def shutdown(self) -> None:
        if self._scheduler and self._scheduler.running:
            try:
                self._scheduler.shutdown(wait=False)
            except RuntimeError:
                # Event loop может быть уже закрыт (например, в тестах)
                pass
            logger.info("JobManager shut down")

    # ── Управление задачами ───────────────────────────────────────────────────

    async def trigger_now(self, name: str, background_tasks: BackgroundTasks) -> str:
        """
        Запускает задачу вручную в обход планировщика через FastAPI BackgroundTasks.
        Не блокирует — возвращает run_id сразу после постановки в очередь.
        """
        entry = next((t for t in get_task_registry() if t["name"] == name), None)
        if entry is None:
            raise KeyError(f"Task '{name}' not found in registry")

        run_id = str(uuid.uuid4())
        background_tasks.add_task(entry["func"], _triggered_by="api", _run_id=run_id)
        return run_id

    def is_running(self, name: str) -> bool:
        return _RUNNING_TASKS.get(name, 0) > 0

    def pause_job(self, name: str) -> None:
        job_id = self._get_scheduler_id(name)
        self._scheduler.pause_job(job_id)

    def resume_job(self, name: str) -> None:
        job_id = self._get_scheduler_id(name)
        self._scheduler.resume_job(job_id)

    def stop_job(self, name: str) -> None:
        job_id = self._get_scheduler_id(name)
        self._scheduler.remove_job(job_id)

    # ── Информация о задачах ──────────────────────────────────────────────────

    def get_registered_tasks(self) -> list[dict[str, Any]]:
        result = []
        for entry in get_task_registry():
            result.append(self._task_info(entry["name"]))
        return result

    def get_task_detail(self, name: str) -> dict[str, Any] | None:
        entry = next((t for t in get_task_registry() if t["name"] == name), None)
        if entry is None:
            return None
        return self._task_info(name)

    async def get_history(
        self, name: str, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        return await get_job_history(self._db_path, name, limit, offset)

    # ── Вспомогательные методы ────────────────────────────────────────────────

    def _task_info(self, name: str) -> dict[str, Any]:
        job_cfg = self._job_configs.get(name)
        aps_job = None
        if self._scheduler and job_cfg and job_cfg.scheduler.id:
            try:
                aps_job = self._scheduler.get_job(job_cfg.scheduler.id)
            except Exception:
                pass

        return {
            "name": name,
            "desc": job_cfg.desc if job_cfg else "",
            "enabled": job_cfg.enabled if job_cfg else False,
            "trigger": job_cfg.trigger if job_cfg else None,
            "running": _RUNNING_TASKS.get(name, 0) > 0,
            "next_run": (
                aps_job.next_run_time.isoformat()
                if aps_job and aps_job.next_run_time
                else None
            ),
            "paused": aps_job.next_run_time is None if aps_job else None,
        }

    def _get_scheduler_id(self, name: str) -> str:
        job_cfg = self._job_configs.get(name)
        if not self._scheduler:
            raise RuntimeError("Планировщик не запущен")
        if not job_cfg or not job_cfg.scheduler.id:
            raise ValueError(
                f"Для задачи '{name}' не задан scheduler.id в конфиге"
            )
        return job_cfg.scheduler.id

    @staticmethod
    def _build_apscheduler_kwargs(job_cfg: JobConfig) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"trigger": job_cfg.trigger}

        if job_cfg.trigger == "cron" and job_cfg.cron:
            c = job_cfg.cron
            kwargs.update(
                minute=c.minute,
                hour=c.hour,
                day=c.day,
                month=c.month,
                day_of_week=c.day_of_week,
                timezone=c.timezone,
            )
        elif job_cfg.trigger == "interval" and job_cfg.interval:
            iv = job_cfg.interval
            if iv.hours:
                kwargs["hours"] = iv.hours
            if iv.minutes:
                kwargs["minutes"] = iv.minutes
            if iv.seconds:
                kwargs["seconds"] = iv.seconds

        s = job_cfg.scheduler
        if s.id:
            kwargs["id"] = s.id
        kwargs["name"] = s.name or job_cfg.desc or job_cfg.name
        kwargs["replace_existing"] = s.replace_existing
        kwargs["max_instances"] = s.max_instances
        kwargs["coalesce"] = s.coalesce
        if s.misfire_grace_time is not None:
            kwargs["misfire_grace_time"] = s.misfire_grace_time

        return kwargs
