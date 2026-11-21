from django import forms

from rooms.models import Room
from .models import User


class EstimateFilterForm(forms.Form):
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
