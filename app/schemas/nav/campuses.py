from pydantic import RootModel


class CampusesLinks(RootModel[list[str]]):
    """
    Корневой JSON:
    [
      "/api/nav/campus?loc=AV",
      "/api/nav/campus?loc=BS",
      ...
    ]
    """
    pass