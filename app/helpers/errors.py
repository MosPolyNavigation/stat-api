class LookupException(Exception):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name} not found"
