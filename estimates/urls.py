from django.urls import path
from . import views

urlpatterns = [
    path("", views.estimates_list, name="estimates_list"),
    path("<int:estimate_id>/", views.estimate_detail, name="estimate_detail"),
]
