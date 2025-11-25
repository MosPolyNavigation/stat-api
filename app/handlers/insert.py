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
    Функция для добавления посещения сайта.

    Эта функция добавляет посещение сайта в базу данных.

    Args:
        db: Сессия базы данных;
        data: Данные посещения сайта.

    Returns:
        Статус операции.
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
    Функция для добавления выбранной аудитории.

    Эта функция добавляет выбранную аудитории в базу данных.

    Args:
        db: Сессия базы данных;
        data: Данные выбранной аудитории.

    Returns:
        Статус операции.
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
    Функция для добавления начатого пути.

    Эта функция добавляет начатый пути в базу данных.

    Args:
        db: Сессия базы данных;
        data: Данные начатого пути.

    Returns:
        Статус операции.
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
    Функция для добавления смененного плана.

    Эта функция добавляет смененный план в базу данных.

    Args:
        db: Сессия базы данных;
        data: Данные смененный плана.

    Returns:
        Статус операции.
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
    Функция для добавления карты этажа.

    Эта функция добавляет карту этажа в базу данных.

    Args:
        db: Сессия базы данных;
        full_file_name: Имя файла с расширением;
        file_path: Путь, по которому сохранен файл;
        campus: Кампус, в котором распологается этаж;
        corpus: Корпус, в котором распологается этаж;
        floor: Номер этажа, в котором распологается этаж.

    Returns:
        Статус операции.
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
