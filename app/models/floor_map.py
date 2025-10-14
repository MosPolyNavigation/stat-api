from sqlalchemy import Column, Integer, String
from app.models.base import Base


class FloorMap(Base):
    """
    Класс для хранения карты этажа.

    Этот класс представляет таблицу "floor_map" в базе данных.

    Attributes:
        id: Идентификатор смененного плана.
        file_name: Имя файла.
        file_extension: Расширение файла.
        file_path: Путь, по которому сохранен файл.
        campus: Кампус, в котором распологается этаж.
        corpus: Корпус, в котором распологается этаж.
        floor: Номер этажа, в котором распологается этаж.
    """

    __tablename__ = "floor_map"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    floor: int = Column(Integer)
    campus: str = Column(String)
    corpus: str = Column(String)
    file_name: str = Column(String, nullable=False)
    file_extension: str = Column(String, nullable=False)
    file_path: str = Column(String, nullable=False)
