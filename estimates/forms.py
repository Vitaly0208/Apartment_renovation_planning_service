from django import forms
from decimal import Decimal
from django.utils import timezone

from rooms.models import Room
from .models import Estimate, User


class EstimateFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, label="Статус",
                               choices=[("", "Все")] + Estimate.Status.choices)
    date = forms.DateField(required=False, label="Дата сметы",
                           widget=forms.DateInput(attrs={"type": "date"}))
    q = forms.CharField(required=False, max_length=200, label="Поиск")
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(), required=False, label="Помещение")
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, label="Заказчик")
    min_total = forms.DecimalField(
        required=False, min_value=0, max_digits=14, decimal_places=2,
        label="Стоимость от")
    max_total = forms.DecimalField(
        required=False, min_value=0, max_digits=14, decimal_places=2,
        label="Стоимость до")
    paid_only = forms.BooleanField(required=False, label="Без бесплатных смет")
    sort = forms.ChoiceField(required=False, label="Сортировка", choices=[
        ("id", "По номеру"), ("total", "По стоимости"),
        ("-total", "Сначала дорогие"), ("room", "По помещению"),
        ("user", "По заказчику"),
    ])

    def clean(self):
        data = super().clean()
        low, high = data.get("min_total"), data.get("max_total")
        if low is not None and high is not None and low > high:
            raise forms.ValidationError("Нижняя граница стоимости превышает верхнюю.")
        return data


class EstimateAdminForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = "__all__"

    def clean(self):
        data = super().clean()
        materials = data.get("materials_cost")
        works = data.get("works_cost")
        if materials is not None and works is not None:
            self.instance.total = materials + works
        return data


class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ("room", "user", "materials", "estimate_date", "status",
                  "materials_cost", "works_cost", "note")
        widgets = {
            "estimate_date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 4}),
        }
        help_texts = {
            "estimate_date": "Дата составления сметы; прошедшая дата допустима.",
            "materials_cost": "Сохранённая стоимость, без пересчёта по каталогу.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select)
                else "form-control")

    def clean_note(self):
        return self.cleaned_data["note"].strip()

    def clean_estimate_date(self):
        value = self.cleaned_data.get("estimate_date")
        if value and value > timezone.localdate():
            raise forms.ValidationError(
                "Дата составления сметы не может быть в будущем.")
        return value

    def clean(self):
        data = super().clean()
        materials, works = data.get("materials_cost"), data.get("works_cost")
        if materials is not None and works is not None:
            total = materials + works
            if total > Decimal("999999999999.99"):
                raise forms.ValidationError(
                    "Итоговая сумма превышает допустимый предел.")
            self.instance.total = total
        return data
