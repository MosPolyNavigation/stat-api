import argparse
import asyncio
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.config import get_settings


EVENT_CODES = ("site", "auds", "ways", "plans")
PAYLOAD_CODES = ("endpoint", "auditory_id", "start_id", "end_id", "success", "plan_id")


def _to_async_dsn(dsn: str) -> str:
    if dsn.startswith("sqlite+aiosqlite://"):
        return dsn
    if dsn.startswith("sqlite://"):
        return dsn.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if dsn.startswith("postgresql+asyncpg://"):
        return dsn
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
    if dsn.startswith("postgres://"):
        return dsn.replace("postgres://", "postgresql+asyncpg://", 1)
    return dsn


def _to_str_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


async def _fetch_mapping(
    conn: AsyncConnection,
    table: str,
    code_column: str = "code_name",
) -> dict[str, int]:
    rows = (
        await conn.execute(
            text(f"SELECT id, {code_column} FROM {table}")
        )
    ).mappings().all()
    return {str(row[code_column]): int(row["id"]) for row in rows}


async def _ensure_new_schema_ready(conn: AsyncConnection) -> None:
    event_types = await _fetch_mapping(conn, "event_types")
    payload_types = await _fetch_mapping(conn, "payload_types")

    missing_event_codes = [code for code in EVENT_CODES if code not in event_types]
    if missing_event_codes:
        raise RuntimeError(
            f"Missing event_types rows for codes: {', '.join(missing_event_codes)}"
        )

    missing_payload_codes = [code for code in PAYLOAD_CODES if code not in payload_types]
    if missing_payload_codes:
        raise RuntimeError(
            f"Missing payload_types rows for codes: {', '.join(missing_payload_codes)}"
        )


async def _ensure_destination_empty(conn: AsyncConnection) -> None:
    counts = (
        await conn.execute(
            text(
                """
                SELECT
                    (SELECT COUNT(*) FROM client_ids) AS client_ids_count,
                    (SELECT COUNT(*) FROM events) AS events_count,
                    (SELECT COUNT(*) FROM payloads) AS payloads_count,
                    (SELECT COUNT(*) FROM reviews) AS reviews_count
                """
            )
        )
    ).mappings().one()

    if any(int(counts[key]) > 0 for key in counts):
        raise RuntimeError(
            "Destination tables are not empty. "
            "This one-time script expects empty client_ids/events/payloads/reviews tables."
        )


async def _insert_client_ids(
    old_conn: AsyncConnection,
    new_conn: AsyncConnection,
) -> dict[str, int]:
    user_rows = (
        await old_conn.execute(
            text(
                """
                SELECT user_id, creation_date
                FROM user_ids
                ORDER BY creation_date, user_id
                """
            )
        )
    ).mappings().all()

    mapping: dict[str, int] = {}
    next_id = 1

    for row in user_rows:
        ident = str(row["user_id"])
        creation_date = row["creation_date"]
        if creation_date is None:
            creation_date = datetime.utcnow()
        if ident in mapping:
            continue

        await new_conn.execute(
            text(
                """
                INSERT INTO client_ids (id, ident, creation_date)
                VALUES (:id, :ident, :creation_date)
                """
            ),
            {"id": next_id, "ident": ident, "creation_date": creation_date},
        )
        mapping[ident] = next_id
        next_id += 1

    return mapping


async def _migrate_events(
    old_conn: AsyncConnection,
    new_conn: AsyncConnection,
    client_map: dict[str, int],
) -> dict[str, int]:
    event_type_map = await _fetch_mapping(new_conn, "event_types")
    payload_type_map = await _fetch_mapping(new_conn, "payload_types")

    event_id = 1
    payload_id = 1
    stats = {
        "site_events": 0,
        "auds_events": 0,
        "ways_events": 0,
        "plans_events": 0,
        "payloads": 0,
        "skipped_rows": 0,
    }

    async def migrate_dataset(
        query: str,
        event_code: str,
        payload_keys: Sequence[str],
        stats_key: str,
    ) -> None:
        nonlocal event_id, payload_id
        rows = (await old_conn.execute(text(query))).mappings().all()
        event_type_id = event_type_map[event_code]

        for row in rows:
            old_user_id = str(row["user_id"])
            client_id = client_map.get(old_user_id)
            if client_id is None:
                stats["skipped_rows"] += 1
                continue

            await new_conn.execute(
                text(
                    """
                    INSERT INTO events (id, client_id, event_type_id, trigger_time)
                    VALUES (:id, :client_id, :event_type_id, :trigger_time)
                    """
                ),
                {
                    "id": event_id,
                    "client_id": client_id,
                    "event_type_id": event_type_id,
                    "trigger_time": row["trigger_time"],
                },
            )

            for payload_key in payload_keys:
                value = row.get(payload_key)
                if value is None:
                    continue

                await new_conn.execute(
                    text(
                        """
                        INSERT INTO payloads (id, event_id, type_id, value)
                        VALUES (:id, :event_id, :type_id, :value)
                        """
                    ),
                    {
                        "id": payload_id,
                        "event_id": event_id,
                        "type_id": payload_type_map[payload_key],
                        "value": _to_str_value(value)[:50],
                    },
                )
                payload_id += 1
                stats["payloads"] += 1

            event_id += 1
            stats[stats_key] += 1

    await migrate_dataset(
        query="""
            SELECT user_id, visit_date AS trigger_time, endpoint
            FROM site_statistics
            ORDER BY visit_date, id
        """,
        event_code="site",
        payload_keys=("endpoint",),
        stats_key="site_events",
    )
    await migrate_dataset(
        query="""
            SELECT user_id, visit_date AS trigger_time, auditory_id, success
            FROM selected_auditories
            ORDER BY visit_date, id
        """,
        event_code="auds",
        payload_keys=("auditory_id", "success"),
        stats_key="auds_events",
    )
    await migrate_dataset(
        query="""
            SELECT user_id, visit_date AS trigger_time, start_id, end_id, success
            FROM started_ways
            ORDER BY visit_date, id
        """,
        event_code="ways",
        payload_keys=("start_id", "end_id", "success"),
        stats_key="ways_events",
    )
    await migrate_dataset(
        query="""
            SELECT user_id, visit_date AS trigger_time, plan_id
            FROM changed_plans
            ORDER BY visit_date, id
        """,
        event_code="plans",
        payload_keys=("plan_id",),
        stats_key="plans_events",
    )

    return stats


async def _migrate_reviews(
    old_conn: AsyncConnection,
    new_conn: AsyncConnection,
    client_map: dict[str, int],
) -> dict[str, int]:
    rows = (
        await old_conn.execute(
            text(
                """
                SELECT
                    id,
                    user_id,
                    text,
                    problem_id,
                    image_name,
                    creation_date,
                    review_status_id
                FROM reviews
                ORDER BY id
                """
            )
        )
    ).mappings().all()

    stats = {"reviews": 0, "skipped_reviews": 0}
    for row in rows:
        client_id = client_map.get(str(row["user_id"]))
        if client_id is None:
            stats["skipped_reviews"] += 1
            continue

        await new_conn.execute(
            text(
                """
                INSERT INTO reviews (
                    id,
                    client_id,
                    text,
                    problem_id,
                    image_name,
                    creation_date,
                    review_status_id
                )
                VALUES (
                    :id,
                    :client_id,
                    :text,
                    :problem_id,
                    :image_name,
                    :creation_date,
                    :review_status_id
                )
                """
            ),
            {
                "id": row["id"],
                "client_id": client_id,
                "text": row["text"],
                "problem_id": row["problem_id"],
                "image_name": row["image_name"],
                "creation_date": row["creation_date"],
                "review_status_id": row["review_status_id"] or 1,
            },
        )
        stats["reviews"] += 1

    return stats


async def _run(old_db_url: str) -> None:
    old_async_url = _to_async_dsn(old_db_url)
    new_async_url = _to_async_dsn(str(get_settings().sqlalchemy_database_url))

    old_engine = create_async_engine(old_async_url)
    new_engine = create_async_engine(new_async_url)

    try:
        async with old_engine.connect() as old_conn, new_engine.begin() as new_conn:
            await _ensure_new_schema_ready(new_conn)
            await _ensure_destination_empty(new_conn)
            client_map = await _insert_client_ids(old_conn, new_conn)
            stats = await _migrate_events(old_conn, new_conn, client_map)
            review_stats = await _migrate_reviews(old_conn, new_conn, client_map)

        print("Migration completed.")
        print(f"Inserted client_ids: {len(client_map)}")
        print(f"Inserted site events: {stats['site_events']}")
        print(f"Inserted auds events: {stats['auds_events']}")
        print(f"Inserted ways events: {stats['ways_events']}")
        print(f"Inserted plans events: {stats['plans_events']}")
        print(f"Inserted payloads: {stats['payloads']}")
        print(f"Skipped rows: {stats['skipped_rows']}")
        print(f"Inserted reviews: {review_stats['reviews']}")
        print(f"Skipped reviews: {review_stats['skipped_reviews']}")
    finally:
        await old_engine.dispose()
        await new_engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-time migration to the new event storage system.",
    )
    parser.add_argument(
        "old_db_url",
        help="Connection string to the old database.",
    )
    args = parser.parse_args()
    asyncio.run(_run(args.old_db_url))


if __name__ == "__main__":
    main()
