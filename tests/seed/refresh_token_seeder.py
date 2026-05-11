from datetime import datetime, timedelta
from app.seed.base_seeder import BaseSeeder
from app.models.auth.user import User
from app.models.auth.refresh_token import RefreshToken


class RefreshTokenSeeder(BaseSeeder):
    """Сидер для создания тестовых refresh токенов."""
    model = RefreshToken

    def gather_data(self):
        now = datetime.now()
        future = now + timedelta(hours=24)

        return [
            {
                "id": 1,
                "user_id": 1,
                "jti": "jti-token-1",
                "exp_date": future,
                "browser": "Chrome 120",
                "user_ip": "192.168.1.1",
                "revoked": False,
                "created_at": now,
            },
            {
                "id": 2,
                "user_id": 1,
                "jti": "jti-token-2",
                "exp_date": future,
                "browser": "Firefox 119",
                "user_ip": "192.168.1.1",
                "revoked": False,
                "created_at": now,
            },
            {
                "id": 3,
                "user_id": 1,
                "jti": "jti-token-3",
                "exp_date": future,
                "browser": "Safari 17",
                "user_ip": "10.0.0.5",
                "revoked": False,
                "created_at": now,
            },
            {
                "id": 4,
                "user_id": 2,
                "jti": "jti-token-4",
                "exp_date": future,
                "browser": "Edge 120",
                "user_ip": "172.16.0.10",
                "revoked": False,
                "created_at": now,
            },
            {
                "id": 5,
                "user_id": 2,
                "jti": "jti-token-5",
                "exp_date": future,
                "browser": "Opera 105",
                "user_ip": "172.16.0.10",
                "revoked": True,  # Отзывенный токен для теста фильтрации
                "created_at": now,
            },
        ]
