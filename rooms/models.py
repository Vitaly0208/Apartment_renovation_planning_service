from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from uuid import uuid4
from .validators import validate_image_size


class Room(models.Model):
    image = models.ImageField("Изображение", upload_to="rooms/%Y/%m/", blank=True,
                              validators=[validate_image_size])
    name = models.CharField("Название", max_length=200)
    length = models.DecimalField("Длина, м", max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])
    width = models.DecimalField("Ширина, м", max_digits=9, decimal_places=2,
                                validators=[MinValueValidator(0.01)])
    height = models.DecimalField("Высота, м", max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])

    slug = models.SlugField("Адрес страницы", max_length=220, unique=True,
                            blank=True, editable=False)
    floor_area_db = models.GeneratedField(
        verbose_name="Площадь пола, м²",
        expression=models.F("length") * models.F("width"),
        output_field=models.DecimalField(max_digits=18, decimal_places=4),
        db_persist=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:180] or "room"
            self.slug = f"{base}-{uuid4().hex}"
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"slug"}
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:room_by_slug", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(length__gt=0, width__gt=0, height__gt=0),
                name="room_positive_dimensions",
            ),
        ]

    @property
    def floor_area(self):
        return self.length * self.width

    @property
    def wall_area(self):
        return 2 * (self.length + self.width) * self.height

    def calculate_floor_area(self):
        return self.floor_area

    def calculate_wall_area(self):
        return self.wall_area

    def __str__(self):
        return self.name
