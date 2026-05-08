from app.models.nav.floor import Floor
from app.seed.base_seeder import BaseSeeder


class FloorSeeder(BaseSeeder):
    model = Floor

    def gather_data(self) -> list[dict[str, int|str]]:
        return [{'id': x+2, 'name': x} for x in range(-1, 10)]
