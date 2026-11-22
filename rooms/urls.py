from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path("create/", views.room_create, name="room_create"),
    path("<int:room_id>/edit/", views.room_edit, name="room_edit"),
    path("by-slug/<slug:slug>/", views.room_by_slug, name="room_by_slug"),
    path("", views.rooms_list, name="rooms_list"),
    path("<int:room_id>/", views.room_detail, name="room_detail"),
    path("available/", views.available_rooms, name="available")
]
