from django.urls import path
from . import views

app_name = "estimates"

urlpatterns = [
    path("", views.estimates_list, name="estimates_list"),
    path("<int:estimate_id>/", views.estimate_detail, name="estimate_detail"),
]
