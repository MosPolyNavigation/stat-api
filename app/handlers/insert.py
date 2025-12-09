"""Обработчики вставки статистики и связанных сущностей."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select
from app import schemas, models
from app.helpers.errors import LookupException
from os import path


async def insert_site_stat(
    db: AsyncSession,
    data: schemas.SiteStatIn
) -> schemas.Status:
    """
    Фиксирует обращение к сайту или API от указанного пользователя.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        data: Данные о посещении (user_id, endpoint).

    Returns:
        schemas.Status: Пустой статус, если запись успешно добавлена.
    """
    user = (await db.execute(
        Select(models.UserId).filter_by(user_id=data.user_id)
    )).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    item = models.SiteStat(user=user, endpoint=data.endpoint)
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_aud_selection(
    db: AsyncSession, data: schemas.SelectedAuditoryIn
) -> schemas.Status:
    """
    Сохраняет выбор аудитории пользователем (успешный или нет).

    Args:
        db: Асинхронная сессия SQLAlchemy.
        data: Входные данные о выбранной аудитории.

    Returns:
        schemas.Status: Пустой статус при успешной записи.
    """
    user = (await db.execute(
        Select(models.UserId).filter_by(user_id=data.user_id)
    )).scalar_one_or_none()
    # auditory = db.execute(
    #     Select(models.Auditory).filter_by(id=data.auditory_id)
    # ).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    # if auditory is None:
    #     raise LookupException("Auditory")
    item = models.SelectAuditory(
        user=user,
        auditory_id=data.auditory_id,
        success=data.success
    )
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_start_way(
    db: AsyncSession,
    data: schemas.StartWayIn
) -> schemas.Status:
    """
    Добавляет попытку построения маршрута между аудиториями.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        data: Входные данные о старте маршрута.

    Returns:
        schemas.Status: Пустой статус при успешной записи.
    """
    user = (await db.execute(
        Select(models.UserId).filter_by(user_id=data.user_id)
    )).scalar_one_or_none()
    # start = db.execute(
    #     Select(models.Auditory).filter_by(id=data.start_id)
    # ).scalar_one_or_none()
    # end = db.execute(
    #     Select(models.Auditory).filter_by(id=data.end_id)
    # ).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    # if start is None:
    #     raise LookupException("Start auditory")
    # if end is None:
    #     raise LookupException("End auditory")
    item = models.StartWay(
        user=user,
        start_id=data.start_id,
        end_id=data.end_id,
        success=data.success
    )
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_changed_plan(
    db: AsyncSession,
    data: schemas.ChangePlanIn
) -> schemas.Status:
    """
    Регистрирует выбор другого плана пользователем.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        data: Данные о смене плана (user_id, plan_id).

    Returns:
        schemas.Status: Пустой статус при успешной записи.
    """
    user = (await db.execute(
        Select(models.UserId).filter_by(user_id=data.user_id)
    )).scalar_one_or_none()
    # plan = db.execute(
    #     Select(models.Plan).filter_by(id=data.plan_id)
    # ).scalar_one_or_none()
    if user is None:
        raise LookupException("User")
    # if plan is None:
    #     raise LookupException("Changed plan")
    item = models.ChangePlan(
        user=user,
        plan_id=data.plan_id
    )
    db.add(item)
    await db.commit()
    return schemas.Status()


async def insert_floor_map(
    db: AsyncSession,
    full_file_name: str,
    file_path: str,
    campus: str,
    corpus: str,
    floor: int
):
    """
    Добавляет новую схему этажа в базу.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        full_file_name: Имя файла вместе с расширением.
        file_path: Относительный путь для публичной раздачи файла.
        campus: Идентификатор кампуса в навигации.
        corpus: Идентификатор корпуса в навигации.
        floor: Номер этажа.

    Returns:
        None: Операция выполняется ради побочного эффекта commit.
    """
    file_name, file_extension = path.splitext(full_file_name)

    item = models.FloorMap(
        floor=floor,
        campus=campus,
        corpus=corpus,
        file_path=file_path,
        file_name=file_name.lower(),
        file_extension=file_extension.lower()
    )

    db.add(item)
    await db.commit()


async def insert_tg_event(
    db: AsyncSession,
    data: schemas.TgBotEventIn
) -> schemas.Status:
    """
    Сохраняет событие из телеграм-бота и обеспечивает наличие связанных сущностей.

    Args:
        db: Асинхронная сессия SQLAlchemy.
        data: Данные события телеграм-бота.

    Returns:
        schemas.Status: Пустой статус при успешной записи.
    """
    tg_user = (
        await db.execute(
            Select(models.TgUser).filter_by(tg_id=data.tg_id)
        )
    ).scalar_one_or_none()
    if tg_user is None:
        tg_user = models.TgUser(tg_id=data.tg_id)
        db.add(tg_user)

    event_type = (
        await db.execute(
            Select(models.TgEventType).filter_by(name=data.event_type)
        )
    ).scalar_one_or_none()
    if event_type is None:
        event_type = models.TgEventType(name=data.event_type)
        db.add(event_type)

    event = models.TgEvent(
        time=data.time,
        tg_user=tg_user,
        event_type=event_type,
        is_dod=data.is_dod
    )
    db.add(event)
    await db.commit()
    return schemas.Status()
