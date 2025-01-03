from pydantic.networks import AnyUrl, UrlConstraints


class SqliteDsn(AnyUrl):
    """A type that will accept any sqlite URL.

    * Host not required
    """
    _constraints = UrlConstraints(allowed_schemes=['sqlite'])
