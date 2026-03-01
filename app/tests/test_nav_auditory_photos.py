"""Tests for auditory photo endpoints in /api/nav."""

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
            data={"aud_id": "1"},
            files=[("photos", ("test.txt", b"text", "text/plain"))],
        )
        assert response.status_code == 415

    def test_200_upload_and_get_links_and_download(self):
        links_before_response = client.get("/api/nav/auditory/1/photos/links")
        assert links_before_response.status_code == 200
        links_before = links_before_response.json()
        assert isinstance(links_before, list)

        upload_response = client.post(
            "/api/nav/auditory/photos/upload",
            headers=ADMIN_HEADERS,
            data={"aud_id": "1"},
            files=[
                ("photos", ("test_1.jpg", b"\xff\xd8\xff", "image/jpeg")),
                ("photos", ("test_2.png", b"\x89PNG\r\n\x1a\n", "image/png")),
            ],
        )
        assert upload_response.status_code == 200

        links_after_response = client.get("/api/nav/auditory/1/photos/links")
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
