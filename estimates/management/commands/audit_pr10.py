import json
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.test import Client, override_settings
from django.test.utils import CaptureQueriesContext

from estimates.models import Estimate, Material, User
from rooms.models import Room


class Command(BaseCommand):
    help = "ПР10: SQL, EXPLAIN и безопасный ORM CRUD с откатом."

    def handle(self, *args, **options):
        result = {"counts": {model.__name__: model.objects.count()
                             for model in (Room, User, Material, Estimate)}}
        for label, queryset in (
                ("naive", Estimate.objects.all()[:5]),
                ("optimized", Estimate.objects.select_related("room", "user")[:5])):
            with CaptureQueriesContext(connection) as queries:
                rows = [(obj.pk, obj.room.name, obj.user.name) for obj in queryset]
            result[label] = {"rows": rows, "count": len(queries),
                             "sql": [q["sql"] for q in queries]}
        with override_settings(ALLOWED_HOSTS=["testserver"], INTERNAL_IPS=[]):
            client = Client()
            pages = ["/", "/rooms/", "/rooms/available/?min_area=1", "/estimates/",
                     "/estimates/?status=ACTIVE&sort=-total&page=2",
                     "/estimates/statistics/"]
            first = Estimate.objects.first()
            if first:
                pages += [f"/estimates/{first.pk}/", first.room.get_absolute_url()]
            result["pages"] = {}
            for url in pages:
                with CaptureQueriesContext(connection) as queries:
                    response = client.get(url)
                result["pages"][url] = {
                    "status": response.status_code, "count": len(queries),
                    "sql": [q["sql"] for q in queries]}
        result["explain"] = Estimate.objects.filter(
            status=Estimate.Status.ACTIVE).explain()
        before = Room.objects.count()
        with transaction.atomic():
            room = Room.objects.create(name="ПР10 временный CRUD", length=2,
                                       width=3, height=2)
            room.name = "ПР10 изменено"
            room.save(update_fields=["name"])
            room.refresh_from_db()
            assert room.name == "ПР10 изменено"
            assert room.floor_area_db == Decimal("6")
            pk = room.pk
            room.delete()
            assert not Room.objects.filter(pk=pk).exists()
            transaction.set_rollback(True)
        result["crud_rolled_back"] = Room.objects.count() == before
        result["admin_accounts"] = self.admin_count()
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))

    @staticmethod
    def admin_count():
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(
            is_superuser=True, is_active=True).count()
