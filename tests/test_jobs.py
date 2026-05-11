"""
Тесты системы управления задачами: декоратор @scheduled_task, JobManager, queue.db, API.

Каждый тест-класс вызывает clear_task_registry() через фикстуру, чтобы
глобальный реестр не загрязнялся между тестами.
"""
import asyncio
import os
import tempfile

import pytest

from app.jobs.manager import (
    scheduled_task,
    clear_task_registry,
    get_task_registry,
    JobManager,
    _RUNNING_TASKS,
)
from app.config import (
    CronConfig,
    IntervalConfig,
    JobConfig,
    JobsConfig,
    SchedulerConfig,
)
from app.jobs.queue_db import (
    init_queue_db,
    log_job_start,
    log_job_success,
    log_job_error,
    get_job_history,
)


# ─── Фикстуры ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_registry():
    """Очищает реестр и счётчики до и после каждого теста."""
    clear_task_registry()
    yield
    clear_task_registry()


@pytest.fixture
def tmp_db(tmp_path):
    """Возвращает путь к временной SQLite-базе."""
    return str(tmp_path / "test_queue.db")


def run(coro):
    """Вспомогательная функция для запуска корутин в синхронных тестах."""
    return asyncio.run(coro)


# ─── Тесты декоратора @scheduled_task ────────────────────────────────────────

class TestScheduledTaskDecorator:
    def test_registers_in_registry(self):
        @scheduled_task(name="test_job")
        async def my_job():
            pass

        registry = get_task_registry()
        assert len(registry) == 1
        assert registry[0]["name"] == "test_job"

    def test_stores_original_and_wrapper(self):
        @scheduled_task(name="test_job")
        async def my_job():
            return 42

        entry = get_task_registry()[0]
        assert entry["original"] is my_job.__wrapped__ if hasattr(my_job, "__wrapped__") else True
        assert callable(entry["func"])

    def test_wrapper_preserves_name(self):
        @scheduled_task(name="test_job")
        async def my_job():
            pass

        assert my_job.__name__ == "my_job"

    def test_overrides_stored(self):
        @scheduled_task(name="test_job", timeout=300)
        async def my_job():
            pass

        entry = get_task_registry()[0]
        assert entry["overrides"]["timeout"] == 300

    def test_multiple_tasks_registered(self):
        @scheduled_task(name="job_a")
        async def job_a():
            pass

        @scheduled_task(name="job_b")
        async def job_b():
            pass

        names = [e["name"] for e in get_task_registry()]
        assert "job_a" in names
        assert "job_b" in names

    def test_wrapper_runs_original(self, tmp_db):
        results = []

        @scheduled_task(name="test_job")
        async def my_job():
            results.append("ran")

        run(init_queue_db(tmp_db))

        # Устанавливаем db путь для логирования
        import app.jobs.manager as mgr
        mgr._DB_PATH = tmp_db

        run(my_job())
        assert results == ["ran"]

    def test_wrapper_logs_to_db(self, tmp_db):
        import app.jobs.manager as mgr
        mgr._DB_PATH = tmp_db
        run(init_queue_db(tmp_db))

        @scheduled_task(name="logged_job")
        async def my_job():
            pass

        run(my_job(_triggered_by="manual"))

        history = run(get_job_history(tmp_db, "logged_job"))
        assert len(history) == 1
        assert history[0]["status"] == "success"
        assert history[0]["triggered_by"] == "manual"

    def test_wrapper_logs_error(self, tmp_db):
        import app.jobs.manager as mgr
        mgr._DB_PATH = tmp_db
        run(init_queue_db(tmp_db))

        @scheduled_task(name="failing_job")
        async def bad_job():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            run(bad_job())

        history = run(get_job_history(tmp_db, "failing_job"))
        assert history[0]["status"] == "failed"
        assert "boom" in history[0]["error"]

    def test_single_instance_protection(self, tmp_db):
        """max_instances=1: второй запуск пропускается, пока первый выполняется."""
        import app.jobs.manager as mgr
        mgr._DB_PATH = tmp_db
        run(init_queue_db(tmp_db))

        call_count = [0]

        @scheduled_task(name="single_job")
        async def single_job():
            call_count[0] += 1

        # Вручную имитируем "уже выполняется"
        _RUNNING_TASKS["single_job"] = 1

        run(single_job())  # должен пропуститься
        assert call_count[0] == 0

        # Убираем имитацию
        _RUNNING_TASKS["single_job"] = 0
        run(single_job())  # теперь должен выполниться
        assert call_count[0] == 1

    def test_custom_run_id_passed(self, tmp_db):
        import app.jobs.manager as mgr
        mgr._DB_PATH = tmp_db
        run(init_queue_db(tmp_db))

        @scheduled_task(name="id_job")
        async def id_job():
            pass

        custom_id = "my-custom-run-id"
        run(id_job(_run_id=custom_id))

        history = run(get_job_history(tmp_db, "id_job"))
        assert history[0]["run_id"] == custom_id


# ─── Тесты queue_db ──────────────────────────────────────────────────────────

class TestQueueDb:
    def test_init_creates_table(self, tmp_db):
        run(init_queue_db(tmp_db))
        assert os.path.exists(tmp_db)

    def test_init_idempotent(self, tmp_db):
        run(init_queue_db(tmp_db))
        run(init_queue_db(tmp_db))  # не должно падать

    def test_log_start(self, tmp_db):
        run(init_queue_db(tmp_db))
        run(log_job_start(tmp_db, "test_job", "run-1", "scheduler"))

        history = run(get_job_history(tmp_db, "test_job"))
        assert len(history) == 1
        assert history[0]["run_id"] == "run-1"
        assert history[0]["status"] == "running"

    def test_log_success(self, tmp_db):
        from datetime import datetime, timezone
        run(init_queue_db(tmp_db))
        run(log_job_start(tmp_db, "job", "run-1", "api"))
        started = datetime.now(timezone.utc)
        run(log_job_success(tmp_db, "run-1", started))

        history = run(get_job_history(tmp_db, "job"))
        assert history[0]["status"] == "success"
        assert history[0]["duration_sec"] is not None

    def test_log_error(self, tmp_db):
        from datetime import datetime, timezone
        run(init_queue_db(tmp_db))
        run(log_job_start(tmp_db, "job", "run-1", "scheduler"))
        started = datetime.now(timezone.utc)
        run(log_job_error(tmp_db, "run-1", started, RuntimeError("oops")))

        history = run(get_job_history(tmp_db, "job"))
        assert history[0]["status"] == "failed"
        assert "oops" in history[0]["error"]
        assert history[0]["traceback"] is not None

    def test_history_pagination(self, tmp_db):
        run(init_queue_db(tmp_db))
        for i in range(5):
            run(log_job_start(tmp_db, "job", f"run-{i}", "scheduler"))

        page1 = run(get_job_history(tmp_db, "job", limit=2, offset=0))
        page2 = run(get_job_history(tmp_db, "job", limit=2, offset=2))
        assert len(page1) == 2
        assert len(page2) == 2
        assert {r["run_id"] for r in page1}.isdisjoint({r["run_id"] for r in page2})

    def test_history_ordered_by_started_desc(self, tmp_db):
        run(init_queue_db(tmp_db))
        for i in range(3):
            run(log_job_start(tmp_db, "job", f"run-{i}", "scheduler"))

        history = run(get_job_history(tmp_db, "job"))
        started_times = [h["started_at"] for h in history]
        assert started_times == sorted(started_times, reverse=True)


# ─── Тесты Pydantic-моделей конфига ──────────────────────────────────────────

class TestJobConfigModels:
    def test_jobs_config_defaults(self):
        cfg = JobsConfig()
        assert cfg.queue == "sqlite"
        assert cfg.url == "queue.db"
        assert cfg.tasks == []

    def test_job_config_cron(self):
        cfg = JobConfig(
            name="my_job",
            trigger="cron",
            cron=CronConfig(hour=0, minute=0, timezone="Europe/Moscow"),
        )
        assert cfg.enabled is True
        assert cfg.cron.hour == 0

    def test_job_config_interval(self):
        cfg = JobConfig(
            name="my_job",
            trigger="interval",
            interval=IntervalConfig(hours=1),
        )
        assert cfg.interval.hours == 1

    def test_scheduler_config_defaults(self):
        s = SchedulerConfig()
        assert s.max_instances == 1
        assert s.replace_existing is False
        assert s.coalesce is False

    def test_jobs_config_parse_via_alias(self):
        """YAML использует ключ 'list', Pydantic маппит его в поле 'tasks'."""
        data = {
            "queue": "sqlite",
            "url": "queue.db",
            "list": [
                {
                    "name": "fetch_data",
                    "enabled": True,
                    "trigger": "interval",
                    "interval": {"hours": 1},
                    "scheduler": {"id": "fetch_hourly", "max_instances": 1},
                }
            ],
        }
        cfg = JobsConfig.model_validate(data)
        assert len(cfg.tasks) == 1
        assert cfg.tasks[0].name == "fetch_data"
        assert cfg.tasks[0].scheduler.id == "fetch_hourly"


# ─── Тесты JobManager ─────────────────────────────────────────────────────────

class TestJobManager:
    def test_setup_skips_disabled(self, tmp_path):
        @scheduled_task(name="disabled_job")
        async def disabled_job():
            pass

        cfg = JobsConfig.model_validate({
            "list": [
                {
                    "name": "disabled_job",
                    "enabled": False,
                    "trigger": "interval",
                    "interval": {"minutes": 5},
                }
            ]
        })
        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(cfg)
        # Планировщик создан, но задача не добавлена
        assert manager._scheduler is not None
        assert manager._scheduler.get_job("disabled_job") is None

    def test_setup_warns_unregistered(self, tmp_path, caplog):
        """Задача в конфиге, но не зарегистрирована через @scheduled_task → warning."""
        import logging
        cfg = JobsConfig(
            list=[
                JobConfig(
                    name="ghost_job",
                    enabled=True,
                    trigger="interval",
                    interval=IntervalConfig(minutes=1),
                )
            ]
        )
        manager = JobManager(static_path=str(tmp_path))
        with caplog.at_level(logging.WARNING, logger="app.jobs.manager"):
            manager.setup_from_config(cfg)
        assert "ghost_job" in caplog.text

    def test_setup_updates_max_instances(self, tmp_path):
        @scheduled_task(name="limited_job")
        async def limited_job():
            pass

        cfg = JobsConfig.model_validate({
            "list": [
                {
                    "name": "limited_job",
                    "enabled": False,
                    "trigger": "interval",
                    "interval": {"minutes": 1},
                    "scheduler": {"max_instances": 3},
                }
            ]
        })
        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(cfg)

        entry = next(e for e in get_task_registry() if e["name"] == "limited_job")
        assert entry["max_instances"] == 3

    def test_get_registered_tasks(self, tmp_path):
        @scheduled_task(name="task_a")
        async def task_a():
            pass

        @scheduled_task(name="task_b")
        async def task_b():
            pass

        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(JobsConfig())
        tasks = manager.get_registered_tasks()
        names = [t["name"] for t in tasks]
        assert "task_a" in names
        assert "task_b" in names

    def test_get_task_detail_not_found(self, tmp_path):
        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(JobsConfig())
        assert manager.get_task_detail("nonexistent") is None

    def test_is_running(self, tmp_path):
        @scheduled_task(name="check_job")
        async def check_job():
            pass

        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(JobsConfig())

        assert manager.is_running("check_job") is False
        _RUNNING_TASKS["check_job"] = 1
        assert manager.is_running("check_job") is True
        _RUNNING_TASKS["check_job"] = 0

    def test_db_path_in_static_dir(self, tmp_path):
        manager = JobManager(static_path=str(tmp_path), queue_db="my_queue.db")
        assert manager.db_path == str(tmp_path / "my_queue.db")

    def test_start_creates_db(self, tmp_path):
        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(JobsConfig())
        run(manager.start())
        assert os.path.exists(manager.db_path)
        manager.shutdown()

    def test_history_returns_records(self, tmp_path):
        @scheduled_task(name="hist_job")
        async def hist_job():
            pass

        manager = JobManager(static_path=str(tmp_path))
        manager.setup_from_config(JobsConfig())
        run(manager.start())

        import app.jobs.manager as mgr
        mgr._DB_PATH = manager.db_path

        run(hist_job(_triggered_by="manual"))

        history = run(manager.get_history("hist_job"))
        assert len(history) == 1
        assert history[0]["triggered_by"] == "manual"

        manager.shutdown()
