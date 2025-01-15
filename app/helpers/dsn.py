from pydantic.networks import AnyUrl, UrlConstraints


class SqliteDsn(AnyUrl):
    """
    Класс для SQLite URL.

    Этот класс представляет тип, который будет принимать любой SQLite URL.

    Attributes:
        _constraints: Ограничения для URL.
    """
    _constraints = UrlConstraints(allowed_schemes=['sqlite'])
