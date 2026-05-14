from pwdlib import PasswordHash
from app.models import User
from app.seed.base_seeder import BaseSeeder


class UserSeeder(BaseSeeder):
    model = User

    def gather_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "login": "admin",
                "hash": PasswordHash.recommended().hash("sidecuter"),
                "token": "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed",
            },
            {
                "id": 2,
                "login": "user_no_perms",
                "hash": PasswordHash.recommended().hash("no_perms"),
                "token": "33e1a4b8-7fa7-4501-9faa-541a5e0ff1ed",
            },
        ]
