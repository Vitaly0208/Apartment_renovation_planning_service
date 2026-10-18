from django.urls import path
from . import views

urlpatterns = [
    path("", views.rooms_list, name="rooms_list"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
]
