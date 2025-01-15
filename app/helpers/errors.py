class LookupException(Exception):
    """
    Класс для ошибок поиска.

    Этот класс представляет исключение, которое возникает при неудачном поиске.

    Attributes:
        name: Имя, которое не было найдено.
    """
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name} not found"
