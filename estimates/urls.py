from django.urls import path
from . import views

app_name = "estimates"

urlpatterns = [
    path("create/", views.estimate_create, name="estimate_create"),
    path("<int:estimate_id>/edit/", views.estimate_edit, name="estimate_edit"),
    path("<int:estimate_id>/cancel/", views.estimate_cancel, name="estimate_cancel"),
    path("", views.estimates_list, name="estimates_list"),
    path("<int:estimate_id>/", views.estimate_detail, name="estimate_detail"),
    path("statistics/", views.statistics, name="statistics")
]
