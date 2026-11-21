from django import forms


class RoomSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=200, label="Название")
    min_area = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2,
        label="Минимальная площадь")
    sort = forms.ChoiceField(required=False, choices=[
        ("name", "По названию"), ("area", "По площади"),
        ("-area", "По убыванию площади")], label="Сортировка")
