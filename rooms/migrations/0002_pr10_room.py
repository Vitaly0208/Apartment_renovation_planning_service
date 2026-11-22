from django.db import migrations, models


def fill_slugs(apps, schema_editor):
    Room = apps.get_model("rooms", "Room")
    from django.utils.text import slugify
    for room in Room.objects.using(schema_editor.connection.alias).all().iterator():
        room.slug = f"{slugify(room.name)[:180] or 'room'}-{room.pk}"
        room.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("rooms", "0001_initial")]
    operations = [
        migrations.AddField("room", "slug", models.SlugField(
            "Адрес страницы", max_length=220, null=True, editable=False)),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField("room", "slug", models.SlugField(
            "Адрес страницы", max_length=220, unique=True, blank=True, editable=False)),
    ]
