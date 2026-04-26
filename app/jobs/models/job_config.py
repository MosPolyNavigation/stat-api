from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class CronConfig(BaseModel):
    minute: str | int = "*"
    hour: str | int = "*"
    day: str | int = "*"
    month: str | int = "*"
    day_of_week: str | int = "*"
    timezone: str = "UTC"


class IntervalConfig(BaseModel):
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class SchedulerConfig(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    replace_existing: bool = False
    max_instances: int = 1
    misfire_grace_time: Optional[int] = None
    coalesce: bool = False


class JobConfig(BaseModel):
    name: str
    enabled: bool = True
    desc: str = ""
    trigger: Literal["cron", "interval"]
    cron: Optional[CronConfig] = None
    interval: Optional[IntervalConfig] = None
    scheduler: SchedulerConfig = SchedulerConfig()


class JobsConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    queue: str = "sqlite"
    url: str = "queue.db"
    # В YAML-конфиге ключ называется "list", но "list" — имя встроенного типа Python
    tasks: list[JobConfig] = Field(default=[], alias="list")
