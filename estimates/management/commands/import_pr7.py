"""Чтение SQLite разрешено только в изолированном импортере старой базы."""
import json
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from rooms.models import Room
from estimates.models import Estimate, Material, User


class Command(BaseCommand):
    help = "Перенести ПР7 в ORM без изменения источника и перезаписи новых данных"

    def add_arguments(self, parser):
        parser.add_argument("--source", type=Path,
                            default=settings.BASE_DIR / "data/renovation.sqlite")
        parser.add_argument("--materials-json", type=Path,
                            default=settings.BASE_DIR / "data/estimates.json")

    @transaction.atomic
    def handle(self, *args, **options):
        source = options["source"].resolve()
        if source == Path(settings.DATABASES["default"]["NAME"]).resolve():
            raise CommandError("Источник и целевая база должны отличаться.")
        try:
            connection = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
            with closing(connection) as conn:
                conn.row_factory = sqlite3.Row
                tables = {name: [dict(row) for row in conn.execute(
                    f"SELECT * FROM {name} ORDER BY id")]
                    for name in ("rooms", "users", "materials", "estimates")}
            links = {}
            if options["materials_json"].exists():
                links = {row["id"]: row for row in json.loads(
                    options["materials_json"].read_text(encoding="utf-8"))}
            else:
                self.stderr.write("JSON отсутствует: материалы не восстановлены.")
            for name, model in (("rooms", Room), ("users", User),
                                ("materials", Material), ("estimates", Estimate)):
                for row in tables[name]:
                    pk = row.pop("id")
                    for field in model._meta.fields:
                        if (field.name in row and not field.generated
                                and field.get_internal_type() == "DecimalField"):
                            row[field.name] = Decimal(str(row[field.name]))
                    if model is Estimate:
                        if not Room.objects.filter(pk=row["room_id"]).exists():
                            raise CommandError(f"Смета {pk}: помещение отсутствует.")
                        if not User.objects.filter(pk=row["user_id"]).exists():
                            raise CommandError(f"Смета {pk}: заказчик отсутствует.")
                    obj, created = model.objects.get_or_create(pk=pk, defaults=row)
                    if not created and any(getattr(obj, key) != value
                                           for key, value in row.items()):
                        raise CommandError(f"Конфликт {name}, id={pk}; импорт отменён.")
                    if model is Estimate and pk in links:
                        old = links[pk]
                        if (old["room_id"], old["user_id"]) != (
                                obj.room_id, obj.user_id):
                            raise CommandError(f"Связи JSON и SQLite различны: {pk}.")
                        ids = set(old.get("material_ids", []))
                        if Material.objects.filter(pk__in=ids).count() != len(ids):
                            raise CommandError(f"Не найдены материалы сметы {pk}.")
                        existing = set(obj.materials.values_list("pk", flat=True))
                        if not created and existing != ids:
                            raise CommandError(f"Конфликт материалов сметы {pk}.")
                        obj.materials.set(ids)
            self.stdout.write(self.style.SUCCESS(
                "Импорт и проверка завершены: " + ", ".join(
                    f"{name}={len(rows)}" for name, rows in tables.items())))
        except (sqlite3.Error, OSError, ValueError, KeyError) as error:
            raise CommandError(f"Импорт отменён: {error}") from error
