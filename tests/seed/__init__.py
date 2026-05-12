from .clientid_seeder import ClientIdSeeder
from .event_seeder import EventSeeder
from .payload_seeder import PayloadSeeder
from .review_seeder import ReviewSeeder
from .user_seeder import UserSeeder
from .user_role_seeder import UserRoleSeeder
from .navigation_seeders import (
    LocationSeeder, CorpusSeeder, PlanSeeder, FloorSeeder,
    TypeSeeder, AuditorySeeder, AudPhotoSeeder
)
# from .dod_seeders import (
#     DodLocationSeeder, DodCorpusSeeder, DodFloorSeeder, DodStaticSeeder,
#     DodPlanSeeder, DodTypeSeeder, DodAuditorySeeder, DodAudPhotoSeeder
# )
from .dashboard_seeder import DashboardSeeder
from .refresh_token_seeder import RefreshTokenSeeder

# Порядок важен из-за внешних ключей
TEST_ONLY_SEEDERS = [
    # Базовые сущности
    ClientIdSeeder(),
    # События и пейлоады (зависят от ClientId, EventType, PayloadType)
    EventSeeder(),
    PayloadSeeder(),
    # Отзывы (зависят от ReviewStatus, Problem, ClientId)
    ReviewSeeder(),
    # Auth (зависят от существующих в app.seed ролей/прав)
    UserSeeder(),
    UserRoleSeeder(),
    # Навигация
    LocationSeeder(), CorpusSeeder(), FloorSeeder(), PlanSeeder(),
    TypeSeeder(), AuditorySeeder(), AudPhotoSeeder(),
    # DOD
    # DodLocationSeeder(), DodCorpusSeeder(), DodFloorSeeder(), DodStaticSeeder(),
    # DodPlanSeeder(), DodTypeSeeder(), DodAuditorySeeder(), DodAudPhotoSeeder(),

    DashboardSeeder(), RefreshTokenSeeder()
]
