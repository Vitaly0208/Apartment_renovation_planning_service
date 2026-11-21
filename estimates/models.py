import math

from django.core.validators import MinValueValidator
from django.db import models


class User(models.Model):
    """Заказчик ремонта; не учётная запись django.contrib.auth."""

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField()

    class Meta:
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=12, decimal_places=2,
                                validators=[MinValueValidator(0)])
    coverage = models.DecimalField(max_digits=12, decimal_places=2,
                                   validators=[MinValueValidator(0.01)])

    class Meta:
        ordering = ["name", "pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0, coverage__gt=0),
                                   name="material_valid_price_coverage"),
        ]

    def calculate_quantity(self, area):
        return math.ceil(area / self.coverage)

    def calculate_cost(self, quantity):
        return round(quantity * self.price, 2)

    def __str__(self):
        return self.name


class Estimate(models.Model):
    room = models.ForeignKey("rooms.Room", on_delete=models.PROTECT,
                             related_name="estimates")
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             related_name="estimates")
    materials = models.ManyToManyField(Material, blank=True,
                                       related_name="estimates")
    materials_cost = models.DecimalField(max_digits=14, decimal_places=2,
                                         default=0, validators=[MinValueValidator(0)])
    works_cost = models.DecimalField(max_digits=14, decimal_places=2,
                                     default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=14, decimal_places=2,
                                default=0, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(materials_cost__gte=0, works_cost__gte=0,
                                   total__gte=0), name="estimate_nonnegative_costs"),
            models.CheckConstraint(
                condition=models.Q(total=models.F("materials_cost")
                                   + models.F("works_cost")),
                name="estimate_total_matches_costs"),
        ]

    def check_budget(self, budget):
        return {"is_sufficient": budget >= self.total,
                "difference": budget - self.total}

    def __str__(self):
        return f"Смета №{self.pk}: {self.total} руб."
