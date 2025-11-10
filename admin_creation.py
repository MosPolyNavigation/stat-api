import argparse
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth.user import User
from app.models.auth.user_role import UserRole

password_hash = PasswordHash.recommended()


def main():
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument("--login", required=True, help="Login for the new admin user")
    parser.add_argument("--password", required=True, help="Password for the new admin user")
    args = parser.parse_args()

    login = args.login
    password = args.password

    connection = get_db()
    db: Session = next(connection)

    try:
        # Проверка, существует ли уже пользователь с таким логином
        existing_user = db.query(User).filter(User.login == login).first()
        if existing_user:
            print(f"User with login '{login}' already exists.")
            return

        # Создание нового пользователя
        user = User()
        user.login = login
        user.hash = password_hash.hash(password)
        user.is_active = True

        db.add(user)
        db.commit()  # Коммитим, чтобы получить user.id
        db.refresh(user)

        # Назначение роли администратора (предполагается, что роль с id=1 — это админ)
        user_role = UserRole()
        user_role.user_id = user.id
        user_role.role_id = 1
        db.add(user_role)
        db.commit()

        print(f"Admin user '{login}' created successfully with role ID 1.")

    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
