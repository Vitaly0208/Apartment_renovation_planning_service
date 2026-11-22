from django.contrib import admin

from estimates.admin import EstimateInline
from .models import Room
from .forms import RoomForm


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomForm
    list_display = ("id", "name", "length", "width", "height", "floor_area_db")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("height",)
    ordering = ("name", "pk")
    list_per_page = 20
    readonly_fields = ("slug", "floor_area_db")
    inlines = (EstimateInline,)
