from pydantic import ConfigDict, BaseModel


class AllowedPermissionsResponse(BaseModel):
    """Схема ответа с допустимыми правами для целей."""

    allowed_permissions: dict[int, list[int]]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"allowed_permissions": {1: [1], 3: [1, 2, 3, 4], 9: [3]}}
        }
    )
