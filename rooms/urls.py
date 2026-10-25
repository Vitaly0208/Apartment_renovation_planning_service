from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("", views.rooms_list, name="rooms_list"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
