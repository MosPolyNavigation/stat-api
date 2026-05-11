from app.models.nav.location import Location
from app.models.nav.corpus import Corpus
from app.models.nav.floor import Floor
from app.models.nav.plan import Plan
from app.models.nav.types import Type
from app.models.nav.auditory import Auditory
from app.models.nav.aud_photo import AudPhoto
from app.seed.base_seeder import BaseSeeder


class LocationSeeder(BaseSeeder):
    model = Location

    def gather_data(self):
        return [{"id": 1, "id_sys": "AV", "name": "Автозаводская", "short": "АВ", "ready": True, "address": "ул. Автозаводская, д. 16", "metro": "Автозаводская"}]


class CorpusSeeder(BaseSeeder):
    model = Corpus

    def gather_data(self):
        return [{"id": 1, "id_sys": "av-test", "loc_id": 1, "name": "Тестовый корпус", "ready": True}]


class PlanSeeder(BaseSeeder):
    model = Plan

    def gather_data(self):
        return [{"id": 1, "id_sys": "test-plan-1", "cor_id": 1, "floor_id": 1, "ready": True, "entrances": "[]", "graph": "[]"}]


class TypeSeeder(BaseSeeder):
    model = Type

    def gather_data(self):
        return [{"id": 1, "name": "Учебная аудитория"}]


class AuditorySeeder(BaseSeeder):
    model = Auditory

    def gather_data(self):
        return [{"id": 1, "id_sys": "test-101", "type_id": 1, "ready": True, "plan_id": 1, "name": "101"}]


class AudPhotoSeeder(BaseSeeder):
    model = AudPhoto

    def gather_data(self):
        return [{"id": 1, "aud_id": 1, "ext": "jpg", "name": "test.jpg", "path": "/tmp/test.jpg", "link": "/api/nav/auditory/photos/test.jpg"}]


class FloorSeeder(BaseSeeder):
    model = Floor

    def gather_data(self):
        return [{"id": 1, "name": 1}]
