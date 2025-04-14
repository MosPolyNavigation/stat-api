from pydantic import ValidationError
from app.schemas import RoomDto, PlanData, RoomData, RoomType
from typing import Optional


def get_corpus_floor_subtitle(plan: PlanData):
    return f"Корпус {plan.corpus.title}, {plan.floor}-й этаж"


def get_title_and_subtitle(in_room: RoomDto, plan):
    if in_room.tabletText and in_room.tabletText != '':
        title = ''
        if in_room.numberOrTitle and in_room.numberOrTitle != '-':
            title = in_room.numberOrTitle
        title += f" — {in_room.tabletText}"
        return title, in_room.addInfo.strip() if in_room.addInfo else ''
    if in_room.type in ['Женский туалет', 'Коворкинг', 'Лифт', 'Мужской туалет', 'Общий туалет', 'Столовая / кафе']:
        return in_room.type, get_corpus_floor_subtitle(plan)
    if in_room.type == 'Лестница':
        if in_room.numberOrTitle and in_room.numberOrTitle != '-':
            title = f"{in_room.numberOrTitle} лестница"
        else:
            title = 'Лестница'
        return title, get_corpus_floor_subtitle(plan)
    if in_room.type == 'Вход в здание':
        return f"Вход в корпус {plan.corpus.title}", ''
    return in_room.numberOrTitle, ''


def fill_room_data(room: RoomDto, plan: PlanData) -> Optional[RoomData]:
    try:
        RoomData.__pydantic_validator__.validate_assignment(RoomData.model_construct(), "type", room.type)
        typ: Optional[RoomType] = RoomType(room.type)
    except ValidationError:
        typ: Optional[RoomType] = None
    title, sub_title = get_title_and_subtitle(room, plan)
    if not room.id.startswith('!'):
        return RoomData(
            id=room.id,
            title=title,
            subTitle=sub_title,
            plan=plan,
            type=typ,
            icon='',
            available=room.available
        )
    else:
        return None
