"""ПР11: формы и реальные HTTP-запросы на отдельной базе и временном media."""
import os
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import django
import pytest
from PIL import Image

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apartment_renovation.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.test.utils import (
    setup_databases, teardown_databases, setup_test_environment,
    teardown_test_environment,
)
from django.urls import reverse
from django.utils import timezone

from estimates.forms import EstimateForm
from estimates.models import Estimate, Material, User
from rooms.models import Room


@pytest.fixture(scope="module", autouse=True)
def database():
    setup_test_environment()
    config = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(config, verbosity=0)
    teardown_test_environment()


def image_upload(name="room.png", color="white"):
    buffer = BytesIO()
    Image.new("RGB", (30, 20), color).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class FormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Кухня", length=5, width=4, height=3)
        cls.user = User.objects.create(name="Анна", phone="123", email="a@example.org")
        cls.material = Material.objects.create(name="Краска", unit="л", price=10,
                                               coverage=5)
        cls.estimate = Estimate.objects.create(room=cls.room, user=cls.user,
                                               materials_cost=10, total=10)
        cls.estimate.materials.add(cls.material)

    def payload(self, **changes):
        data = {"room": self.room.pk, "user": self.user.pk,
                "materials": [self.material.pk], "materials_cost": "12.35",
                "works_cost": "20.10", "status": "DRAFT",
                "estimate_date": timezone.localdate().isoformat(),
                "note": "  Уточнить цвет\nстен  "}
        data.update(changes)
        return data

    def test_get_forms_initial_values_and_empty_post(self):
        count = Estimate.objects.count()
        for url in ("/estimates/create/", f"/estimates/{self.estimate.pk}/edit/",
                    "/rooms/create/", f"/rooms/{self.room.pk}/edit/"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "csrfmiddlewaretoken")
        response = self.client.get(f"/estimates/{self.estimate.pk}/edit/")
        self.assertEqual(response.context["form"].instance.pk, self.estimate.pk)
        response = self.client.post("/estimates/create/", {})
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Estimate.objects.count(), count)

    def test_create_calculates_total_and_saves_materials(self):
        response = self.client.post("/estimates/create/", self.payload(total="1"))
        obj = Estimate.objects.latest("pk")
        self.assertRedirects(response, f"/estimates/{obj.pk}/")
        self.assertEqual(obj.total, Decimal("32.45"))
        self.assertEqual(list(obj.materials.all()), [self.material])
        self.assertEqual(obj.note, "Уточнить цвет\nстен")
        self.assertEqual(obj.room_id, self.room.pk)
        self.assertEqual(obj.user_id, self.user.pk)

    def test_edit_updates_existing_row_and_m2m(self):
        count = Estimate.objects.count()
        response = self.client.post(f"/estimates/{self.estimate.pk}/edit/",
                                    self.payload(materials=[], works_cost="30"))
        self.assertEqual(response.status_code, 302)
        self.estimate.refresh_from_db()
        self.assertEqual(Estimate.objects.count(), count)
        self.assertEqual(self.estimate.total, Decimal("42.35"))
        self.assertEqual(self.estimate.materials.count(), 0)

    def test_invalid_input_retains_values_and_does_not_write(self):
        tomorrow = (timezone.localdate() + timedelta(days=1)).isoformat()
        invalid = [dict(materials_cost="-1"), dict(works_cost="NaN"),
                   dict(status="WRONG"), dict(room=999999), dict(user=999999),
                   dict(materials=[999999]), dict(estimate_date="bad"),
                   dict(estimate_date=tomorrow), dict(note="x" * 2001),
                   dict(note="bad\x01note"),
                   dict(materials_cost="999999999999.99", works_cost="1")]
        count = Estimate.objects.count()
        for changes in invalid:
            with self.subTest(changes=changes):
                response = self.client.post(f"/estimates/{self.estimate.pk}/edit/",
                                            self.payload(**changes))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertContains(response, "Уточнить" if "note" not in changes else "textarea")
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.total, 10)
        self.assertEqual(self.estimate.materials.count(), 1)
        self.assertEqual(Estimate.objects.count(), count)

    def test_past_optional_date_and_multiple_estimates_are_allowed(self):
        for value in ("2000-01-01", ""):
            form = EstimateForm(self.payload(estimate_date=value))
            self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(self.client.post("/estimates/create/", self.payload()).status_code, 302)
        self.assertEqual(Estimate.objects.filter(room=self.room).count(), 2)

    def test_cancel_post_only_preserves_data_and_is_repeatable(self):
        url = f"/estimates/{self.estimate.pk}/cancel/"
        self.assertEqual(self.client.get(url).status_code, 405)
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.status, Estimate.Status.DRAFT)
        for _ in range(2):
            self.assertEqual(self.client.post(url).status_code, 302)
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.status, Estimate.Status.CANCELLED)
        self.assertEqual(self.estimate.total, 10)
        self.assertEqual(self.estimate.materials.count(), 1)
        response = self.client.get("/estimates/", {"status": "CANCELLED"})
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_csrf_for_all_mutations(self):
        client = Client(enforce_csrf_checks=True)
        urls = ("/estimates/create/", f"/estimates/{self.estimate.pk}/edit/",
                f"/estimates/{self.estimate.pk}/cancel/", "/rooms/create/",
                f"/rooms/{self.room.pk}/edit/")
        for url in urls:
            self.assertEqual(client.post(url, self.payload()).status_code, 403)
        client.get("/estimates/create/")
        token = client.cookies["csrftoken"].value
        response = client.post("/estimates/create/", self.payload(), HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 302)

    def test_missing_objects_and_unsupported_methods(self):
        for path in ("/estimates/999999/edit/", "/rooms/999999/edit/"):
            self.assertEqual(self.client.get(path).status_code, 404)
            self.assertEqual(self.client.post(path, {}).status_code, 404)
        self.assertEqual(self.client.post("/estimates/999999/cancel/").status_code, 404)
        self.assertEqual(self.client.put("/estimates/create/").status_code, 405)

    def test_note_is_escaped(self):
        self.client.post(f"/estimates/{self.estimate.pk}/edit/",
                         self.payload(note="<script>alert(1)</script>"))
        response = self.client.get(f"/estimates/{self.estimate.pk}/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_room_image_upload_replace_clear_and_no_image(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            data = {"name": "Гостиная", "length": "6", "width": "5", "height": "3"}
            response = self.client.post("/rooms/create/", {**data, "image": image_upload()})
            room = Room.objects.latest("pk")
            self.assertRedirects(response, room.get_absolute_url())
            self.assertTrue(Path(room.image.path).is_file())
            self.assertContains(self.client.get(room.get_absolute_url()), room.image.url)
            old_name, slug = room.image.name, room.slug
            url = f"/rooms/{room.pk}/edit/"
            self.client.post(url, {**data, "image": image_upload(color="blue")})
            room.refresh_from_db()
            self.assertNotEqual(room.image.name, old_name)
            self.assertTrue(Path(room.image.path).is_file())
            self.assertEqual(room.slug, slug)
            self.assertEqual(room.floor_area_db, 30)
            self.client.post(url, {**data, "image-clear": "on"})
            room.refresh_from_db()
            self.assertFalse(room.image)
            self.assertContains(self.client.get(room.get_absolute_url()), "пока не загружено")

    def test_invalid_image_and_dimensions_do_not_write(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            data = {"name": "Комната", "length": "5", "width": "4", "height": "3"}
            fake = SimpleUploadedFile("fake.png", b"not an image", content_type="image/png")
            large = image_upload()
            large = SimpleUploadedFile("large.png", large.read() + b"0" * (6 * 1024 * 1024),
                                       content_type="image/png")
            for changes in ({"image": fake}, {"image": large}, {"length": "0"}):
                response = self.client.post("/rooms/create/", {**data, **changes})
                self.assertTrue(response.context["form"].errors)
            self.assertEqual(Room.objects.count(), 1)
            self.assertEqual(list(Path(directory).rglob("*")), [])

    def test_admin_upload_uses_same_image_validation(self):
        admin = get_user_model().objects.create_superuser("admin", password="test-password")
        self.client.force_login(admin)
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            response = self.client.post(reverse("admin:rooms_room_add"), {
                "name": "Спальня", "length": "3", "width": "4", "height": "3",
                "image": image_upload(), "estimates-TOTAL_FORMS": "0",
                "estimates-INITIAL_FORMS": "0", "estimates-MIN_NUM_FORMS": "0",
                "estimates-MAX_NUM_FORMS": "1000", "_save": "Сохранить",
            })
            self.assertEqual(response.status_code, 302)
            room = Room.objects.latest("pk")
            self.assertTrue(Path(room.image.path).is_file())
