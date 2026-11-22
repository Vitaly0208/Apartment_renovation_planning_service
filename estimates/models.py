import math

from django.core.validators import MinValueValidator
from django.db import models
from .validators import validate_note


class User(models.Model):
    """Заказчик ремонта; не учётная запись django.contrib.auth."""

    name = models.CharField("Имя заказчика", max_length=200)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Электронная почта")

    class Meta:
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField("Название", max_length=200)
    unit = models.CharField("Единица измерения", max_length=30)
    price = models.DecimalField("Цена, руб.", max_digits=12, decimal_places=2,
                                validators=[MinValueValidator(0)])
    coverage = models.DecimalField("Покрытие, м²", max_digits=12, decimal_places=2,
                                   validators=[MinValueValidator(0.01)])

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
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


class EstimateQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Estimate.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=Estimate.Status.CANCELLED)

    def completed(self):
        return self.filter(status=Estimate.Status.COMPLETED)

    def for_date(self, date):
        return self.filter(estimate_date=date)


class Estimate(models.Model):
    note = models.TextField("Примечание", max_length=2000, blank=True,
                            validators=[validate_note])

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Черновик"
        ACTIVE = "ACTIVE", "Согласована"
        CANCELLED = "CANCELLED", "Отменена"
        COMPLETED = "COMPLETED", "Выполнена"

    objects = EstimateQuerySet.as_manager()
    status = models.CharField("Статус", max_length=10, choices=Status.choices,
                              default=Status.DRAFT)
    estimate_date = models.DateField("Дата сметы", null=True, blank=True)

    room = models.ForeignKey("rooms.Room", verbose_name="Помещение",
                             on_delete=models.PROTECT,
                             related_name="estimates")
    user = models.ForeignKey(User, verbose_name="Заказчик", on_delete=models.PROTECT,
                             related_name="estimates")
    materials = models.ManyToManyField(Material, verbose_name="Материалы",
                                       blank=True,
                                       related_name="estimates")
    materials_cost = models.DecimalField("Материалы, руб.", max_digits=14,
                                         decimal_places=2,
                                         default=0, validators=[MinValueValidator(0)])
    works_cost = models.DecimalField("Работы, руб.", max_digits=14, decimal_places=2,
                                     default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField("Итого, руб.", max_digits=14, decimal_places=2,
                                default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Смета"
        verbose_name_plural = "Сметы"
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["DRAFT", "ACTIVE", "CANCELLED", "COMPLETED"]),
                name="estimate_valid_status"),
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
