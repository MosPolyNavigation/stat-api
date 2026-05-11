from enum import Enum


class Problem(str, Enum):
    def __str__(self):
        return str(self.value)

    PLAN = "plan"
    WORK = "work"
    WAY = "way"
    OTHER = "other"
