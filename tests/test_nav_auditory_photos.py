"""Tests for auditory photo endpoints in /api/nav."""

import base64
from .base import client

ADMIN_TOKEN = "11e1a4b8-7fa7-4501-9faa-541a5e0ff1ed"
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


class TestNavAuditoryPhotos:
    def test_401_upload_requires_auth(self):
        response = client.post(
            "/api/nav/auditory/photos/upload",
            data={"aud_id": "1"},
            files=[("photos", ("test.jpg", b"\xff\xd8\xff", "image/jpeg"))],
        )
        assert response.status_code == 401

    def test_404_upload_auditory_not_found(self):
        response = client.post(
            "/api/nav/auditory/photos/upload",
            headers=ADMIN_HEADERS,
            data={"aud_id": "99999"},
            files=[("photos", ("test.jpg", b"\xff\xd8\xff", "image/jpeg"))],
        )
        assert response.status_code == 404

    def test_415_upload_rejects_non_image(self):
        response = client.post(
            "/api/nav/auditory/photos/upload",
            headers=ADMIN_HEADERS,
            data={"aud_id": "test-101"},
            files=[("photos", ("test.txt", b"text", "text/plain"))],
        )
        assert response.status_code == 415

    def test_200_upload_and_get_links_and_download(self):
        links_before_response = client.get("/api/nav/auditory/test-101/photos/links")
        assert links_before_response.status_code == 200
        links_before = links_before_response.json()
        assert isinstance(links_before, list)

        upload_response = client.post(
            "/api/nav/auditory/photos/upload",
            headers=ADMIN_HEADERS,
            data={"aud_id": "test-101"},
            files=[
                ("photos", ("test_1.jpg", b"\xff\xd8\xff", "image/jpeg")),
                ("photos", ("test_2.png", b"\x89PNG\r\n\x1a\n", "image/png")),
            ],
        )
        assert upload_response.status_code == 200

        links_after_response = client.get("/api/nav/auditory/test-101/photos/links")
        assert links_after_response.status_code == 200
        links_after = links_after_response.json()
        assert isinstance(links_after, list)
        assert len(links_after) >= len(links_before) + 2

        new_links = links_after[len(links_before):]
        assert len(new_links) == 2
        for link in new_links:
            assert isinstance(link, str)
            assert link.startswith("/api/nav/auditory/photos/")

        image_response = client.get(new_links[0])
        assert image_response.status_code == 200
        assert len(image_response.content) > 0

    def test_404_thumbnails_auditory_not_found(self):
        """Тест: 404 при попытке получить thumbnails для несуществующей аудитории."""
        response = client.get("/api/nav/auditory/99999/thumbnails")
        assert response.status_code == 404

    def test_200_thumbnails_returns_dict(self):
        """Тест: 200 эндпоинт возвращает словарь."""
        # Проверяем, что эндпоинт возвращает валидный словарь
        response = client.get("/api/nav/auditory/test-101/thumbnails")
        assert response.status_code == 200
        thumbnails = response.json()
        assert isinstance(thumbnails, dict)

    def test_200_upload_creates_thumbnails(self):
        """Тест: 200 при загрузке фото создаются thumbnails и доступны через эндпоинт."""
        # Создаем валидное JPEG изображение (минимальное)
        jpeg_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c'
            b'\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
            b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00'
            b'\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01'
            b'\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05'
            b'\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04'
            b'\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A'
            b'\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82'
            b'\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwx'
            b'yz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a'
            b'\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba'
            b'\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda'
            b'\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8'
            b'\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xff\xd9'
        )

        # Загружаем изображение
        upload_response = client.post(
            "/api/nav/auditory/photos/upload",
            headers=ADMIN_HEADERS,
            data={"aud_id": "test-101"},
            files=[("photos", ("test_thumbnail.jpg", jpeg_data, "image/jpeg"))],
        )
        assert upload_response.status_code == 200

        # Получаем thumbnails
        thumbnails_response = client.get("/api/nav/auditory/test-101/thumbnails")
        assert thumbnails_response.status_code == 200
        thumbnails = thumbnails_response.json()
        assert isinstance(thumbnails, dict)
        assert len(thumbnails) > 0

        # Проверяем, что каждый thumbnail валиден
        for thumbnail_name, base64_data in thumbnails.items():
            assert isinstance(thumbnail_name, str)
            assert thumbnail_name.endswith(".jpg")
            assert isinstance(base64_data, str)
            assert len(base64_data) > 0

            # Проверяем, что данные валидно декодируются из base64
            try:
                decoded_data = base64.b64decode(base64_data)
                assert len(decoded_data) > 0
                # Проверяем JPEG сигнатуру
                assert decoded_data[:2] == b'\xff\xd8'
            except Exception as e:
                raise AssertionError(f"Failed to decode thumbnail {thumbnail_name}: {e}")
