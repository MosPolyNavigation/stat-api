from pydantic import Field, ConfigDict


class UserIdBase:
    user_id: str = Field(title="id",
                         description="Unique user id",
                         min_length=36,
                         max_length=36,
                         pattern=r"[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{8}")


class FromOrmBase:
    model_config = ConfigDict(from_attributes=True)
