from django.core.validators import MinValueValidator
from django.db import models


class Room(models.Model):
    name = models.CharField("Название", max_length=200)
    length = models.DecimalField(max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])
    width = models.DecimalField(max_digits=9, decimal_places=2,
                                validators=[MinValueValidator(0.01)])
    height = models.DecimalField(max_digits=9, decimal_places=2,
                                 validators=[MinValueValidator(0.01)])

    class Meta:
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
