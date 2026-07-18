from app.schemas.filter import FilterSvobodn
from app.schemas.rasp.schedule import Schedule, Auditory, Rasp, Day, Lesson


def filter_lesson(lesson: Lesson | None, filter_: FilterSvobodn) -> Lesson:
    """
    Фильтрует список занятий по датам.

    Логика: возвращает только те занятия, которые пересекаются с заданным диапазоном.
    """
    if not lesson:
        return []

    # Если задан диапазон дат — оставляем только пересекающиеся занятия
    if filter_.end_date is not None:
        return [
            variety
            for variety in lesson
            # Пересечение: занятие начинается до конца фильтра И заканчивается после начала фильтра
            if variety.dt <= filter_.end_date and variety.df >= filter_.start_date
        ]

    # Если только start_date — проверяем, попадает ли момент в занятие
    # (для случаев, когда несколько занятий на одну пару в разное время)
    return [
        variety for variety in lesson if variety.dt <= filter_.start_date <= variety.df
    ]


def filter_day(day: Day | None, filter_: FilterSvobodn) -> Day:
    """
    Фильтрует расписание дня по парам и датам.
    Возвращает структуру {para_number: filtered_lessons}.
    """
    if day is None:
        return {str(num): [] for num in range(1, 8)}

    if filter_.para is not None:
        para_key = str(filter_.para)
        return {para_key: filter_lesson(day.get(para_key), filter_)}

    # Если пара не указана — фильтруем все 7 пар
    return {str(num): filter_lesson(day.get(str(num)), filter_) for num in range(1, 8)}


def filter_auditory(aud: Auditory, filter_: FilterSvobodn) -> Auditory:
    """
    Фильтрует расписание одной аудитории по дню/дате/паре.
    """
    # Собираем отфильтрованные дни в dict для model_construct
    filtered_days: dict[str, Day | None] = {}
    _ = filtered_days
    days_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

    if filter_.day is not None:
        # Фильтруем только указанный день
        day_name = filter_.day.name
        day_data = getattr(aud.rasp, day_name, None)
        filtered_days = {
            name: filter_day(day_data, filter_) if name == day_name else None
            for name in days_names
        }
    else:
        # Фильтруем все дни
        filtered_days = {
            name: filter_day(getattr(aud.rasp, name, None), filter_)
            for name in days_names
        }

    # Создаём новый Rasp через model_construct (обходит валидацию, но сохраняет типизацию)
    filtered_rasp = Rasp.model_construct(**filtered_days)

    return Auditory.model_construct(id=aud.id, link=aud.link, rasp=filtered_rasp)


def filter_svobodn(schedule: Schedule, filter_: FilterSvobodn) -> Schedule:
    """
    Фильтрует всё расписание по аудиториям.
    """
    return {
        aud_id: filter_auditory(auditory, filter_)
        for aud_id, auditory in schedule.items()
        if auditory is not None  # Явная проверка вместо truthiness
    }
