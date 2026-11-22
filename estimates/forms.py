from django import forms

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
