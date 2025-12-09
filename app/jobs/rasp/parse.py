"""Парсер расписания групп в структуру Schedule."""

import re
import asyncio
from datetime import date
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from app.jobs.rasp.canonize import is_valid, canonize
from app.jobs.rasp.get_schedule import get_schedule
from app.schemas.rasp.dto import Dto, DayDto, LessonDto, VarietyDto
from app.schemas.rasp.schedule import Schedule, Variety, Auditory, Rasp
from app.models.nav.auditory import Auditory as AuditoryModel

filter_reg = re.compile(
    r'(گُگ?|گْگّگ>|cگُگ?‘?‘'|گ?گ?گ>گّگüگ?|گ>گّگüگ?|‘"گçگ?گç‘?گّگ>‘?گ?گّ‘?|گٌگ?گّ‘?|hami|گ?گّگ?گٌ|‘'گç‘:گ?گ?گ?‘?گّگ?|گ+گٌگ?گَگ?گ?گ+گٌگ?گّ‘'|‘?گَگ?گ>گَگ?گ?گ?|گ+گٌگ?‘'گç‘:گ?گ?گ>گ?گ?گٌگٌ|h'
    r'گّگ?گٌ|گ?گç‘?‘'گçگ>‘?گ?گ?‘?‘'‘?|گ+گّگْ‘< گُ‘?گّگَ‘'گٌگَ|گ'گّگْ‘< گُ‘?گّگَ‘'گٌگَ)',
    re.IGNORECASE)

numToDay = {"1": "monday", "2": "tuesday", "3": "wednesday", "4": "thursday", "5": "friday", "6": "saturday"}


class AsyncQueueIterator:
    """Асинхронный итератор для обхода очереди с результатами загрузки расписания."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    def __aiter__(self):
        return self

    async def __anext__(self):
        item: Union[tuple[str, Union[Dto, None]], None] = await self.queue.get()
        if item is None:
            raise StopAsyncIteration
        return item


def parse_variety(day: str, lesson: str, variety_dto: VarietyDto, group_name: str, schedule: Schedule):
    """
    Разбирает конкретный вариант занятия и записывает его в расписание.

    Args:
        day: Номер дня в формате строки.
        lesson: Номер пары.
        variety_dto: DTO варианта занятия.
        group_name: Название группы.
        schedule: Формируемое расписание.

    Returns:
        None: Заполняет переданный словарь schedule.
    """
    global filter_reg
    global numToDay
    if any(filter_reg.search(aud) for aud in variety_dto.shortRooms):
        return
    auditories = [canonize(variety_dto.location, aud) for aud in variety_dto.shortRooms]
    variety = Variety(
        dt=date.fromisoformat(variety_dto.dt),
        df=date.fromisoformat(variety_dto.df),
        dts=variety_dto.dts,
        groupType="study",
        groupNames=[group_name],
        discipline=variety_dto.sbj,
        teachers=variety_dto.teacher.split(', ')
    )
    for auditory_id in auditories:
        if auditory_id not in schedule:
            schedule[auditory_id] = Auditory(id=auditory_id, rasp=Rasp())

        day_name = numToDay.get(day)
        if not day_name:
            return

        rasp = schedule[auditory_id].rasp
        day_schedule = getattr(rasp, day_name)
        if day_schedule is None:
            day_schedule = {}
            setattr(rasp, day_name, day_schedule)

        if lesson not in day_schedule:
            day_schedule[lesson] = []
        day_schedule[lesson].append(variety)


def parse_lesson(day: str, lesson: str, lesson_dto: LessonDto, group_name: str, schedule: Schedule):
    """
    Обрабатывает все варианты для одной пары.

    Args:
        day: Номер дня.
        lesson: Номер пары.
        lesson_dto: DTO пары с вариантами.
        group_name: Название группы.
        schedule: Формируемое расписание.

    Returns:
        None
    """
    for varietyDto in lesson_dto:
        if not is_valid(varietyDto.location):
            continue
        parse_variety(day, lesson, varietyDto, group_name, schedule)


def parse_day(day: str, day_dto: DayDto, group_name: str, schedule: Schedule):
    """
    Обрабатывает расписание на день для конкретной группы.

    Args:
        day: Номер дня.
        day_dto: DTO дня с парами.
        group_name: Название группы.
        schedule: Формируемое расписание.

    Returns:
        None
    """
    for lesson, lessonDto in day_dto.items():
        parse_lesson(day, lesson, lessonDto, group_name, schedule)


def parse_dto(group: str, dto: Dto, schedule: Schedule):
    """
    Разбирает DTO расписания группы по всем дням.

    Args:
        group: Код группы.
        dto: DTO расписания.
        schedule: Формируемое расписание.

    Returns:
        None
    """
    for day, dayDto in dto.grid.items():
        parse_day(day, dayDto, group, schedule)


async def parse(db: AsyncSession) -> Schedule:
    """
    Загружает расписание для всех групп и приводит его к структуре Schedule.

    Args:
        db: Асинхронная сессия SQLAlchemy.

    Returns:
        Schedule: Словарь аудиторий с расписанием по дням и парам.
    """
    schedule: Schedule = {}
    queue = asyncio.Queue()

    async def loader():
        async for group, dto in get_schedule():
            await queue.put((group, dto))
        await queue.put(None)

    async def parser():
        async for group, dto in AsyncQueueIterator(queue):
            if not dto:
                continue
            parse_dto(group, dto, schedule)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(loader())
        tg.create_task(parser())

    for aud in schedule.values():
        aud.rasp.merge()
        aud.link = (await db.execute(Select(AuditoryModel.link).filter_by(id_sys=aud.id))).scalars().first()
    return schedule
