import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .constants import LOCMEM_CACHE

MEDIA_DIR = tempfile.mkdtemp()


@override_settings(CACHES=LOCMEM_CACHE, MEDIA_ROOT=MEDIA_DIR)
class ProtectedMediaTests(TestCase):
    """Driver photos are not public: only admin staff can open them."""

    @classmethod
    def setUpTestData(cls):
        (Path(MEDIA_DIR) / "drivers").mkdir(exist_ok=True)
        (Path(MEDIA_DIR) / "drivers" / "photo.jpg").write_bytes(b"jpeg")

    def test_anonymous_is_sent_to_admin_login(self):
        response = self.client.get("/media/drivers/photo.jpg")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_staff_can_open_photo(self):
        staff = get_user_model().objects.create_user("operator", password="pass12345", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get("/media/drivers/photo.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"jpeg")

    def test_path_cannot_leave_media_root(self):
        staff = get_user_model().objects.create_user("operator", password="pass12345", is_staff=True)
        self.client.force_login(staff)
        # serve() treats ../ as a suspicious path (400)
        self.assertIn(self.client.get("/media/../settings.py").status_code, (400, 404))
