import traceback
from datetime import datetime, timezone

import aiosqlite

_CREATE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS job_runs (
    run_id      TEXT PRIMARY KEY,
    job_name    TEXT NOT NULL,
    status      TEXT NOT NULL CHECK(status IN ('running', 'success', 'failed')),
    started_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    duration_sec REAL,
    error       TEXT,
    traceback   TEXT,
    triggered_by TEXT CHECK(triggered_by IN ('scheduler', 'manual', 'api')),
    meta        TEXT
);
CREATE INDEX IF NOT EXISTS idx_job_runs_name    ON job_runs(job_name);
CREATE INDEX IF NOT EXISTS idx_job_runs_started ON job_runs(started_at);
"""


async def init_queue_db(db_path: str) -> None:
    """Создаёт таблицу job_runs и индексы, если их ещё нет."""
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(_CREATE_SCHEMA_SQL)
        await db.commit()


async def log_job_start(db_path: str, job_name: str, run_id: str, triggered_by: str) -> None:
    """Записывает строку о старте задачи со статусом 'running'."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            INSERT INTO job_runs (run_id, job_name, status, triggered_by)
            VALUES (?, ?, 'running', ?)
            """,
            (run_id, job_name, triggered_by),
        )
        await db.commit()


async def log_job_success(db_path: str, run_id: str, started_at: datetime) -> None:
    """Обновляет статус на 'success', записывает время завершения и длительность."""
    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            UPDATE job_runs
            SET status = 'success', finished_at = ?, duration_sec = ?
            WHERE run_id = ?
            """,
            (finished_at.isoformat(), duration, run_id),
        )
        await db.commit()


async def log_job_error(db_path: str, run_id: str, started_at: datetime, exc: Exception) -> None:
    """Обновляет статус на 'failed', записывает ошибку и traceback."""
    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()
    tb = traceback.format_exc()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            UPDATE job_runs
            SET status = 'failed', finished_at = ?, duration_sec = ?,
                error = ?, traceback = ?
            WHERE run_id = ?
            """,
            (finished_at.isoformat(), duration, str(exc), tb, run_id),
        )
        await db.commit()


async def get_job_history(
    db_path: str,
    job_name: str,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Возвращает историю запусков задачи из queue.db, сортировка по убыванию времени."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM job_runs
            WHERE job_name = ?
            ORDER BY started_at DESC
            LIMIT ? OFFSET ?
            """,
            (job_name, limit, offset),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
