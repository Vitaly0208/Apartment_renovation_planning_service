"""ПР10: реальные HTTP-сценарии админки, статусы, миграции и SQL."""
import os
from datetime import date
from decimal import Decimal

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apartment_renovation.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection, IntegrityError, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.test.utils import (
    setup_databases, teardown_databases, setup_test_environment,
    teardown_test_environment, CaptureQueriesContext,
)
from django.urls import reverse

from estimates.models import Estimate, User, Material
from rooms.models import Room


@pytest.fixture(scope="module", autouse=True)
def database():
    setup_test_environment()
    config = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(config, verbosity=0)
    teardown_test_environment()


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            "test-admin", "admin@example.org", "Test-password-123")
        cls.room = Room.objects.create(name="Кухня", length=5, width=4, height=3)
        cls.user = User.objects.create(name="Анна", phone="123", email="a@example.org")
        cls.material = Material.objects.create(name="Краска", unit="л", price=10,
                                               coverage=5)
        cls.estimate = Estimate.objects.create(
            room=cls.room, user=cls.user, total=30, materials_cost=10, works_cost=20,
            status=Estimate.Status.ACTIVE, estimate_date=date(2026, 11, 22))
        cls.estimate.materials.add(cls.material)

    def test_permissions(self):
        url = reverse("admin:estimates_estimate_changelist")
        self.assertEqual(self.client.get(url).status_code, 302)
        staff = get_user_model().objects.create_user("staff", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_lists_search_filters_and_inlines(self):
        self.client.force_login(self.admin)
        for model in (Room, User, Material, Estimate):
            opts = model._meta
            response = self.client.get(reverse(
                f"admin:{opts.app_label}_{opts.model_name}_changelist"))
            self.assertEqual(response.status_code, 200)
        url = reverse("admin:estimates_estimate_changelist")
        response = self.client.get(url, {"q": "Анна", "status__exact": "ACTIVE"})
        self.assertEqual(response.context["cl"].result_count, 1)
        response = self.client.get(url, {"status__exact": "CANCELLED"})
        self.assertEqual(response.context["cl"].result_count, 0)
        for model, obj in (("rooms_room", self.room), ("estimates_user", self.user)):
            response = self.client.get(reverse(f"admin:{model}_change", args=[obj.pk]))
            self.assertContains(response, "Смета")
            self.assertContains(response, reverse(
                "admin:estimates_estimate_change", args=[self.estimate.pk]))

    def payload(self, **changes):
        data = {"room": self.room.pk, "user": self.user.pk,
                "estimate_date": "2026-11-22", "status": "COMPLETED",
                "materials_cost": "40", "works_cost": "60",
                "materials": [self.material.pk], "_save": "Сохранить"}
        data.update(changes)
        return data

    def test_admin_create_update_delete_and_total(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("admin:estimates_estimate_add"), self.payload())
        self.assertEqual(response.status_code, 302)
        obj = Estimate.objects.latest("pk")
        self.assertEqual(obj.total, Decimal("100"))
        url = reverse("admin:estimates_estimate_change", args=[obj.pk])
        response = self.client.post(url, self.payload(works_cost="80"))
        self.assertEqual(response.status_code, 302)
        obj.refresh_from_db()
        self.assertEqual(obj.total, Decimal("120"))
        self.assertEqual(obj.materials.count(), 1)
        response = self.client.post(reverse("admin:estimates_estimate_delete",
                                           args=[obj.pk]), {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Estimate.objects.filter(pk=obj.pk).exists())

    def test_invalid_admin_input_does_not_write(self):
        self.client.force_login(self.admin)
        url = reverse("admin:estimates_estimate_change", args=[self.estimate.pk])
        for data in (self.payload(materials_cost="-1"), self.payload(status="WRONG"),
                     self.payload(estimate_date="bad")):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["adminform"].form.errors)
        self.estimate.refresh_from_db()
        self.assertEqual(self.estimate.total, 30)

    def test_status_date_pagination_and_statistics(self):
        for amount in range(7):
            Estimate.objects.create(room=self.room, user=self.user, total=amount,
                                    works_cost=amount, status=Estimate.Status.ACTIVE,
                                    estimate_date=date(2026, 11, 22))
        response = self.client.get("/estimates/", {
            "status": "ACTIVE", "date": "2026-11-22", "sort": "-total", "page": 2})
        self.assertEqual(response.context["page_obj"].paginator.count, 8)
        self.assertContains(response, "status=ACTIVE")
        self.assertContains(response, "date=2026-11-22")
        for params in ({"date": "bad"}, {"status": "WRONG"}):
            response = self.client.get("/estimates/", params)
            self.assertTrue(response.context["form"].errors)
            self.assertEqual(response.context["page_obj"].paginator.count, 0)
        self.estimate.status = Estimate.Status.CANCELLED
        self.estimate.save(update_fields=["status"])
        self.assertEqual(Estimate.objects.active().for_date(date(2026, 11, 22)).count(), 7)
        self.assertEqual(Estimate.objects.cancelled().count(), 1)
        self.assertEqual(Estimate.objects.completed().count(), 0)
        summary = self.client.get("/estimates/statistics/").context["summary"]
        self.assertEqual((summary["active"], summary["cancelled"]), (7, 1))

    def test_slug_generated_area_and_context(self):
        self.room.refresh_from_db()
        self.assertEqual(self.room.floor_area_db, Decimal("20"))
        slug = self.room.slug
        response = self.client.get(self.room.get_absolute_url())
        self.assertContains(response, "Кухня")
        self.assertEqual(response.context["rooms_count"], 1)
        self.room.length = 6
        self.room.save()
        self.room.refresh_from_db()
        self.assertEqual(self.room.floor_area_db, Decimal("24"))
        self.assertEqual(self.room.slug, slug)
        other = Room.objects.create(name="Кухня", length=1, width=1, height=1)
        self.assertNotEqual(other.slug, slug)
        self.assertEqual(self.client.get("/rooms/by-slug/missing/").status_code, 404)
        self.assertEqual(self.client.get(f"/rooms/{self.room.pk}/").status_code, 200)

    def test_related_queries_and_explain(self):
        with self.assertNumQueries(1):
            obj = Estimate.objects.select_related("room", "user").get(pk=self.estimate.pk)
            self.assertEqual((obj.room.name, obj.user.name), ("Кухня", "Анна"))
        for _ in range(6):
            Estimate.objects.create(room=self.room, user=self.user)
        counts = []
        for page in (1, 2):
            with CaptureQueriesContext(connection) as queries:
                self.client.get("/estimates/", {"page": page})
            counts.append(len(queries))
        self.assertEqual(counts[0], counts[1])
        self.assertTrue(Estimate.objects.filter(room=self.room).explain())
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Estimate.objects.filter(pk=self.estimate.pk).update(status="WRONG")


class MigrationTests(TransactionTestCase):
    def test_pr9_data_survives_migration(self):
        executor = MigrationExecutor(connection)
        old = [("rooms", "0001_initial"), ("estimates", "0001_initial")]
        latest = executor.loader.graph.leaf_nodes()
        executor.migrate(old)
        apps = executor.loader.project_state(old).apps
        room = apps.get_model("rooms", "Room").objects.create(
            name="Кухня", length=5, width=4, height=3)
        user = apps.get_model("estimates", "User").objects.create(
            name="Анна", phone="123", email="a@example.org")
        material = apps.get_model("estimates", "Material").objects.create(
            name="Краска", unit="л", price=10, coverage=5)
        estimate = apps.get_model("estimates", "Estimate").objects.create(
            room=room, user=user, materials_cost=200, works_cost=500, total=700)
        estimate.materials.add(material)
        try:
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            migrated = Estimate.objects.get(pk=estimate.pk)
            self.assertEqual(migrated.total, 700)
            self.assertEqual(migrated.status, Estimate.Status.DRAFT)
            self.assertIsNone(migrated.estimate_date)
            self.assertEqual(migrated.materials.count(), 1)
            self.assertEqual(migrated.room.slug, f"room-{room.pk}")
            self.assertEqual(migrated.room.floor_area_db, Decimal("20"))
        finally:
            MigrationExecutor(connection).migrate(latest)
