from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase, override_settings

from apps.drivers.models import Driver

from .constants import LOCMEM_CACHE
from .functions import make_driver


@override_settings(CACHES=LOCMEM_CACHE)
class DriverAdminPasswordTests(TestCase):
    """The admin sets a driver's password, never the raw hash."""

    def setUp(self):
        admin_user = get_user_model().objects.create_superuser("admin", "admin@example.com", "admin-pass")
        self.client.force_login(admin_user)
        self.driver = make_driver("DRV-AAAAA1")

    def change_url(self):
        return f"/api/admin/drivers/driver/{self.driver.id}/change/"

    def form_data(self, **extra):
        data = {
            "full_name": self.driver.full_name,
            "phone_number": self.driver.phone_number,
            "car_model": "Cobalt",
            "car_color": "White",
            "car_number": self.driver.car_number,
            "status": "OFFLINE",
            "is_approved": "on",
        }
        data.update(extra)
        return data

    def test_hash_field_is_not_on_the_form(self):
        response = self.client.get(self.change_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="password_hash"')
        self.assertContains(response, 'name="new_password"')

    def test_new_password_is_hashed_and_ends_sessions(self):
        response = self.client.post(self.change_url(), self.form_data(new_password="brand-new-1"))
        self.assertEqual(response.status_code, 302, getattr(response, "context", None) and response.context["adminform"].form.errors)

        self.driver.refresh_from_db()
        self.assertTrue(check_password("brand-new-1", self.driver.password_hash))
        self.assertEqual(self.driver.token_version, 1)

    def test_empty_password_keeps_the_old_one(self):
        old_hash = self.driver.password_hash
        response = self.client.post(self.change_url(), self.form_data())
        self.assertEqual(response.status_code, 302)

        self.driver.refresh_from_db()
        self.assertEqual(self.driver.password_hash, old_hash)
        self.assertEqual(self.driver.token_version, 0)

    def test_drivers_added_in_admin_get_a_login_code(self):
        # driver_code is read-only in the admin; before, every added driver got "" and the
        # second one failed on the unique constraint
        for n in (1, 2):
            response = self.client.post("/api/admin/drivers/driver/add/", self.form_data(
                full_name=f"Admin Driver {n}", phone_number=f"+99890000000{n}",
                car_number=f"01B00{n}AA", new_password="secret123",
            ))
            self.assertEqual(response.status_code, 302)

        added = Driver.objects.filter(full_name__startswith="Admin Driver")
        codes = {d.driver_code for d in added}
        self.assertEqual(len(codes), 2)
        self.assertTrue(all(code.startswith("DRV-") for code in codes))
        # The new driver can log in with the code and the password set in the admin
        response = self.client.post(
            "/api/drivers/login/", {"driver_code": added[0].driver_code, "password": "secret123"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_new_driver_requires_a_password(self):
        response = self.client.post("/api/admin/drivers/driver/add/", self.form_data(
            phone_number="+998900000009", car_number="01B009AA",
        ))
        self.assertEqual(response.status_code, 200)  # form shown again with the error
        self.assertFalse(Driver.objects.filter(phone_number="+998900000009").exists())
