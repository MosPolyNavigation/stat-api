import re
from transliterate import translit

AV_REG = re.compile(r'ав(?P<cor>\d)(?P<num>\d{3})/?(?P<sub>[а-я]|\d)?', re.IGNORECASE)
PR_REG = re.compile(r'пр ?(?:.*[(])?(?P<cor>\d)(?P<num>\d{3}) ?(?P<sub>[а-я](?![а-я]{3}))?', re.IGNORECASE)
M_REG = re.compile(r'м((?P<cor>\d)(?P<num>\d{3}))?\s?(?P<sub>[а-я]{1,6})?', re.IGNORECASE)
PK_REG = re.compile(r'пк(?P<num>\d{3})[( ]?(?P<sub>[а-я])?', re.IGNORECASE)
BS_REG = re.compile(r'(?P<cor>а|б|в|нд|н)-?(?P<num>\d{1,3})?(?P<sub>[а-я]{1,3})?', re.IGNORECASE)


def av(aud: str):
    global AV_REG
    match = AV_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for av")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"av{nums}{sub}".lower()


def pr(aud: str):
    global PR_REG
    match = PR_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for pr")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"pr{nums}{sub}".lower()


def m(aud: str):
    global M_REG
    match = M_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for m")
    groups = match.groupdict()
    nums = f"-{groups['cor']}{groups['num']}" if groups['cor'] and groups['num'] else ""
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"m{nums}{sub}".lower()


def pk(aud: str):
    global PK_REG
    match = PK_REG.search(aud)
    if not match:
        raise ValueError("Invalid input for pk")
    groups = match.groupdict()
    nums = f"-{groups['num']}"
    sub = f"-{translit(groups['sub'], 'ru', reversed=True)}" if groups['sub'] else ""
    return f"pk{nums}{sub}".lower()


def bs(aud: str):
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
    "автозаводская",
    "большая семеновская",
    "михалковская",
    "прянишникова",
    "павла корчагина"
]

PATTERNS = {
    "автозаводская": av,
    "большая семеновская": bs,
    "михалковская": m,
    "прянишникова": pr,
    "павла корчагина": pk
}


def is_valid(location: str):
    global LOCATION_NAMES
    return any(True for loc in LOCATION_NAMES if location.strip().lower() == loc)


def canonize(location: str, auditory: str):
    global PATTERNS
    return PATTERNS[location.strip().lower()](auditory)
