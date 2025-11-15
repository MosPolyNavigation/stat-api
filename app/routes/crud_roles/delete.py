from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.helpers.permissions import require_rights
from app.models.auth.role import Role


def register_endpoint(router: APIRouter):
    "Эндпоинт для удаления роли"

    @router.delete(
        "/{role_id}",
        description="Удаление роли",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_rights("roles", "delete"))]
    )
    async def delete_role(
        role_id: int,
        db: Session = Depends(get_db)
    ):
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(404, "Роль не найдена")

        db.delete(role)
        db.commit()

        return {"message": f"Роль {role_id} удалена", "role_id": role_id}
