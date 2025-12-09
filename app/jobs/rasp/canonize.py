"""Канонизация обозначений аудиторий в расписании."""

import re
from transliterate import translit

AV_REG = re.compile(r'گّگ?(?P<cor>\d)(?P<num>\d{3})/?(?P<sub>[گّ-‘?]|\d)?', re.IGNORECASE)
PR_REG = re.compile(r'گُ‘? ?(?:.*[(])?(?P<cor>\d)(?P<num>\d{3}) ?(?P<sub>[گّ-‘?](?![گّ-‘?]{3}))?', re.IGNORECASE)
M_REG = re.compile(r'گ?((?P<cor>\d)(?P<num>\d{3}))?\s?(?P<sub>[گّ-‘?]{1,6})?', re.IGNORECASE)
PK_REG = re.compile(r'گُگَ(?P<num>\d{3})[( ]?(?P<sub>[گّ-‘?])?', re.IGNORECASE)
BS_REG = re.compile(r'(?P<cor>گّ|گ+|گ?|گ?گ?|گ?)-?(?P<num>\d{1,3})?(?P<sub>[گّ-‘?]{1,3})?', re.IGNORECASE)


def av(aud: str):
    """
    Приводит название аудитории ав к виду av-{корпус}{номер}[-суффикс].

    Args:
        aud: Исходная строка аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global AV_REG
    match = AV_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for av")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"av{nums}{sub}".lower()


def pr(aud: str):
    """
    Приводит аудиторию корпуса ПР к каноническому виду pr-{корпус}{номер}[-суффикс].

    Args:
        aud: Исходная строка аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global PR_REG
    match = PR_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for pr")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"pr{nums}{sub}".lower()


def m(aud: str):
    """
    Канонизирует аудиторию М формата m-{корпус}{номер}[-суффикс].

    Args:
        aud: Исходная строка аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global M_REG
    match = M_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for m")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}" if groups['cor'] and groups['num'] else ""
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"m{nums}{sub}".lower()


def pk(aud: str):
    """
    Канонизирует аудиторию ПК к виду pk-{номер}[-суффикс].

    Args:
        aud: Исходная строка аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global PK_REG
    match = PK_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for pk")
    groups = match.groupdict()
    nums = f"-{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"pk{nums}{sub}".lower()


def bs(aud: str):
    """
    Канонизирует аудиторию БС, добавляя корпус/номер/суффикс.

    Args:
        aud: Исходная строка аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global BS_REG
    match = BS_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for bs")
    groups = match.groupdict()
    cor = translit(groups['cor'], 'ru', reversed=True)
    nums = f"-{groups['num']}" if groups['num'] else ""
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"{cor}{nums}{sub}".lower()


LOCATION_NAMES = [
    "گّگ?‘'گ?گْگّگ?گ?گ?‘?گَگّ‘?",
    "گ+گ?گ>‘?‘?گّ‘? ‘?گçگ?گçگ?گ?گ?‘?گَگّ‘?",
    "گ?گٌ‘:گّگ>گَگ?گ?‘?گَگّ‘?",
    "گُ‘?‘?گ?گٌ‘?گ?گٌگَگ?گ?گّ",
    "گُگّگ?گ>گّ گَگ?‘?‘طگّگ?گٌگ?گّ"
]

PATTERNS = {
    "گّگ?‘'گ?گْگّگ?گ?گ?‘?گَگّ‘?": av,
    "گ+گ?گ>‘?‘?گّ‘? ‘?گçگ?گçگ?گ?گ?‘?گَگّ‘?": bs,
    "گ?گٌ‘:گّگ>گَگ?گ?‘?گَگّ‘?": m,
    "گُ‘?‘?گ?گٌ‘?گ?گٌگَگ?گ?گّ": pr,
    "گُگّگ?گ>گّ گَگ?‘?‘طگّگ?گٌگ?گّ": pk
}


def is_valid(location: str):
    """
    Проверяет, что переданное название локации поддерживается.

    Args:
        location: Название локации.

    Returns:
        bool: True, если локация распознается.
    """
    global LOCATION_NAMES
    return any(True for loc in LOCATION_NAMES if location.strip().lower() == loc)


def canonize(location: str, auditory: str):
    """
    Приводит обозначение аудитории к единому виду в зависимости от локации.

    Args:
        location: Название локации.
        auditory: Исходное обозначение аудитории.

    Returns:
        str: Каноническое имя аудитории.
    """
    global PATTERNS
    return PATTERNS[location.strip().lower()](auditory)
