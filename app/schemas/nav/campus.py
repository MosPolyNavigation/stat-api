from typing import Any

from pydantic import BaseModel

type PlanLink = str
type PlanLinks = list[PlanLink]
type StairsGroup = list[str]
type StairsGroups = list[StairsGroup]
type Crossings = list[Any]


class CorpusNav(BaseModel):
    """
    Описание одного корпуса в CAMPUS-{loc}.json
    """
    rusName: str
    planLinks: PlanLinks
    stairsGroups: StairsGroups

# Динамический словарь корпусов, ключ = id_sys корпуса
type Corpuses = dict[str, CorpusNav]

class CampusNav(BaseModel):
    """
    Весь CAMPUS-{loc}.json
    """
    id: str
    rusName: str
    corpuses: Corpuses
    crossings: Crossings
