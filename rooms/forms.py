from django import forms
from .models import Room


class RoomSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=200, label="Название")
    min_area = forms.DecimalField(
        required=False, min_value=0, max_digits=12, decimal_places=2,
        label="Минимальная площадь")
    sort = forms.ChoiceField(required=False, choices=[
        ("name", "По названию"), ("area", "По площади"),
        ("-area", "По убыванию площади")], label="Сортировка")


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ("name", "length", "width", "height", "image")
        help_texts = {"image": "JPEG, PNG или WebP, не более 5 МБ."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "image"):
            if image.image.format not in {"JPEG", "PNG", "WEBP"}:
                raise forms.ValidationError("Выберите изображение JPEG, PNG или WebP.")
        return image
