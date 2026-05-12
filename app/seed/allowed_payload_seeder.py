from app.models.event import AllowedPayload
from app.seed.base_seeder import BaseSeeder
from app.constants import ALLOWED_PAYLOADS


class AllowedPayloadSeeder(BaseSeeder):
    model = AllowedPayload
    pk_fields = ("event_type_id", "payload_type_id")

    def gather_data(self) -> list[dict[str, int]]:
        return [
            {"event_type_id": evt_id, "payload_type_id": pl_id}
            for evt_id, pl_id in ALLOWED_PAYLOADS
        ]
