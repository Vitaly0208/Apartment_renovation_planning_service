"""Интеграционные проверки ПР9 на отдельной тестовой базе Django."""
import os
from decimal import Decimal
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sqlite3
from contextlib import closing

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apartment_renovation.settings")
django.setup()

from django.core.management import call_command, CommandError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.test.utils import setup_databases, teardown_databases
from django.test.utils import setup_test_environment, teardown_test_environment

from rooms.models import Room
from estimates.models import Estimate, Material, User


@pytest.fixture(scope="module", autouse=True)
def orm_database():
    setup_test_environment()
    config = setup_databases(verbosity=0, interactive=False)
    yield
    teardown_databases(config, verbosity=0)
    teardown_test_environment()


class ORMTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.room = Room.objects.create(name="Kitchen", length=5, width=4, height=3)
        cls.empty_room = Room.objects.create(name="Bath", length=2, width=2, height=3)
        cls.user = User.objects.create(name="Alice", phone="123", email="a@example.org")
        cls.empty_user = User.objects.create(name="Bob", phone="456", email="b@ex.org")
        cls.material = Material.objects.create(name="Paint", unit="l", price=10,
                                               coverage=5)
        for cost in range(0, 80, 10):
            e = Estimate.objects.create(room=cls.room, user=cls.user,
                                        materials_cost=cost, total=cost)
            e.materials.add(cls.material)

    def test_crud_and_protected_relations(self):
        room = Room.objects.create(name="Test", length=1, width=2, height=3)
        room.name = "Updated"
        room.save()
        self.assertEqual(Room.objects.get(pk=room.pk).name, "Updated")
        room.delete()
        self.assertFalse(Room.objects.filter(name="Updated").exists())
        with self.assertRaises(ProtectedError):
            self.room.delete()
        self.assertEqual(self.room.estimates.count(), 8)
        self.assertEqual(self.user.estimates.count(), 8)
        self.assertEqual(self.material.estimates.count(), 8)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Room.objects.create(name="Bad", length=0, width=1, height=1)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            Estimate.objects.create(room=self.room, user=self.user, total=1)

    def test_pages_areas_and_related_data(self):
        for url in ("/", "/rooms/", f"/rooms/{self.room.pk}/", "/estimates/",
                    "/estimates/statistics/"):
            self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get(f"/rooms/{self.room.pk}/")
        self.assertContains(response, "20")
        self.assertContains(response, "54")
        first = Estimate.objects.first()
        with self.assertNumQueries(2):
            response = self.client.get(f"/estimates/{first.pk}/")
        self.assertContains(response, "Alice")
        self.assertContains(response, "Kitchen")
        self.assertContains(response, "Paint")
        for url in ("/rooms/999999/", "/estimates/999999/"):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_search_filters_order_and_pagination(self):
        response = self.client.get("/rooms/available/", {"min_area": 10, "q": "kit"})
        self.assertEqual(list(response.context["rooms"]), [self.room])
        response = self.client.get("/rooms/", {"q": "zz"})
        self.assertEqual(list(response.context["rooms"]), [])
        params = {"room": self.room.pk, "user": self.user.pk, "min_total": 10,
                  "max_total": 70, "paid_only": "on", "q": "ali", "sort": "-total"}
        response = self.client.get("/estimates/", params)
        self.assertEqual(response.context["page_obj"].paginator.count, 7)
        self.assertEqual([e["total"] for e in response.context["estimates"]],
                         [70, 60, 50, 40, 30])
        self.assertContains(response, "page=2")
        self.assertContains(response, "sort=-total")
        self.assertContains(response, "q=ali")
        params["page"] = 2
        response = self.client.get("/estimates/", params)
        self.assertEqual([e["total"] for e in response.context["estimates"]], [20, 10])
        for value, expected in (("abc", 1), ("999", 2), ("-1", 2)):
            params["page"] = value
            response = self.client.get("/estimates/", params)
            self.assertEqual(response.context["page_obj"].number, expected)
        response = self.client.get("/estimates/", {"q": "example.org"})
        self.assertEqual(response.context["page_obj"].paginator.count, 8)

    def test_invalid_parameters(self):
        for params in ({"min_area": "abc"}, {"min_area": "-1"},
                       {"min_area": "NaN"}, {"sort": "password"}):
            response = self.client.get("/rooms/available/", params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
        for params in ({"room": "-1"}, {"user": "x"}, {"min_total": "NaN"},
                       {"min_total": 20, "max_total": 10}, {"sort": "invalid"}):
            response = self.client.get("/estimates/", params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].errors)
            self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_statistics_includes_objects_without_estimates(self):
        response = self.client.get("/estimates/statistics/")
        summary = response.context["summary"]
        self.assertEqual(summary["count"], 8)
        self.assertEqual(summary["total_sum"], Decimal("280"))
        self.assertEqual(summary["average"], 35)
        self.assertEqual(summary["minimum"], 0)
        self.assertEqual(summary["maximum"], 70)
        bob = next(row for row in response.context["stats"] if row.pk == self.empty_user.pk)
        self.assertEqual(bob.estimates_count, 0)
        self.assertEqual(bob.total_spent, 0)
        self.assertContains(response, "Bath")


class ImportTests(TestCase):
    def test_import_repeat_and_conflict_rollback(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "old.sqlite"
            links = Path(directory) / "estimates.json"
            with closing(sqlite3.connect(source)) as conn:
                conn.executescript(Path("sql/schema.sql").read_text(encoding="utf-8"))
                conn.execute("INSERT INTO rooms VALUES (10, 'Test', 2, 3, 4)")
                conn.execute("INSERT INTO users VALUES (10, 'User', '1', 'old@ex.org')")
                conn.execute("INSERT INTO materials VALUES (10, 'Wood', 'm', 20, 2)")
                conn.execute("INSERT INTO estimates VALUES (10, 10, 10, 20, 30, 50)")
                conn.commit()
            links.write_text(json.dumps([{"id": 10, "room_id": 10, "user_id": 10,
                                          "material_ids": [10]}]), encoding="utf-8")
            original = source.read_bytes()
            for _ in range(2):
                call_command("import_pr7", source=source, materials_json=links,
                             stdout=StringIO())
            self.assertEqual(Room.objects.count(), 1)
            self.assertEqual(Estimate.objects.get(pk=10).materials.get().pk, 10)
            self.assertEqual(source.read_bytes(), original)
            with closing(sqlite3.connect(source)) as conn:
                conn.execute("INSERT INTO rooms VALUES (11, 'New', 2, 3, 4)")
                conn.execute("UPDATE estimates SET total=100 WHERE id=10")
                conn.commit()
            with self.assertRaises(CommandError):
                call_command("import_pr7", source=source, materials_json=links,
                             stdout=StringIO())
            self.assertFalse(Room.objects.filter(pk=11).exists())
            self.assertEqual(Estimate.objects.get(pk=10).total, 50)
