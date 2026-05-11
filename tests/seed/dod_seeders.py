# from app.models.dod.location import DodLocation
# from app.models.dod.corpus import DodCorpus
# from app.models.dod.floor import DodFloor
# from app.models.dod.static import DodStatic
# from app.models.dod.plan import DodPlan
# from app.models.dod.types import DodType
# from app.models.dod.auditory import DodAuditory
# from app.models.dod.aud_photo import DodAudPhoto
# from app.seed.base_seeder import BaseSeeder
#
#
# class DodLocationSeeder(BaseSeeder):
#     model = DodLocation
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "id_sys": "DD",
#                 "name": "DOD Campus",
#                 "short": "DD",
#                 "ready": True,
#                 "address": "dod address",
#                 "metro": "dod metro"
#             }
#         ]
#
#
# class DodCorpusSeeder(BaseSeeder):
#     model = DodCorpus
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "id_sys": "dd-test",
#                 "loc_id": 1,
#                 "name": "DOD Corpus",
#                 "ready": True
#             }
#         ]
#
#
# class DodFloorSeeder(BaseSeeder):
#     model = DodFloor
#
#     def gather_data(self):
#         return [{"id": 1, "name": 1}]
#
#
# class DodStaticSeeder(BaseSeeder):
#     model = DodStatic
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "ext": "svg",
#                 "path": "/dod/plan.svg",
#                 "name": "dod-plan-svg",
#                 "link": "/static/dod-plan.svg"
#             }
#         ]
#
#
# class DodPlanSeeder(BaseSeeder):
#     model = DodPlan
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "id_sys": "dod-plan-1",
#                 "cor_id": 1,
#                 "floor_id": 1,
#                 "ready": True,
#                 "entrances": "[]",
#                 "graph": "{}",
#                 "svg_id": 1
#             }
#         ]
#
#
# class DodTypeSeeder(BaseSeeder):
#     model = DodType
#
#     def gather_data(self):
#         return [{"id": 1, "name": "DOD Type"}]
#
#
# class DodAuditorySeeder(BaseSeeder):
#     model = DodAuditory
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "id_sys": "dod-101",
#                 "type_id": 1,
#                 "ready": True,
#                 "plan_id": 1,
#                 "name": "D101"
#             }
#         ]
#
#
# class DodAudPhotoSeeder(BaseSeeder):
#     model = DodAudPhoto
#
#     def gather_data(self):
#         return [
#             {
#                 "id": 1,
#                 "aud_id": 1,
#                 "ext": "png",
#                 "name": "dod.png",
#                 "path": "/tmp/dod.png",
#                 "link": "/api/dod/auditory/photos/dod.png"
#             }
#         ]
