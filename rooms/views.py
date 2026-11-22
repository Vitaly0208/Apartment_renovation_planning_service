from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import RoomForm, RoomSearchForm
from .models import Room


@require_http_methods(["GET", "POST"])
def room_create(request):
    return room_form(request)


@require_http_methods(["GET", "POST"])
def room_edit(request, room_id):
    return room_form(request, get_object_or_404(Room, pk=room_id))


def room_form(request, room=None):
    form = RoomForm(request.POST if request.method == "POST" else None,
                    request.FILES if request.method == "POST" else None,
                    instance=room)
    if request.method == "POST" and form.is_valid():
        room = form.save()
        messages.success(request, "Помещение сохранено.")
        return redirect(room.get_absolute_url())
    return render(request, "rooms/room_form.html", {"form": form, "room": room})


def room_queryset(request):
    form = RoomSearchForm(request.GET)
    rooms = Room.objects.all()
    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            rooms = rooms.filter(name__icontains=data["q"])
        if data["min_area"] is not None:
            rooms = rooms.alias(area=F("length") * F("width")).filter(
                area__gte=data["min_area"])
        area = F("length") * F("width")
        sorting = {"name": ("name", "pk"), "area": (area, "pk"),
                   "-area": (area.desc(), "pk")}
        rooms = rooms.order_by(*sorting.get(data["sort"], sorting["name"]))
    else:
        rooms = rooms.none()
    return form, rooms


def rooms_list(request):
    form, rooms = room_queryset(request)
    return render(request, "rooms/room_list.html", {"rooms": rooms, "form": form})


def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, "rooms/room_detail.html", {
        "room": room, "estimates": room.estimates.select_related("user"),
    })


def available_rooms(request):
    form, rooms = room_queryset(request)
    if not request.GET:
        rooms = rooms.none()
    return render(request, "rooms/available.html", {
        "rooms": rooms, "form": form, "searched": bool(request.GET),
    })


def room_by_slug(request, slug):
    room = get_object_or_404(Room, slug=slug)
    return render(request, "rooms/room_detail.html", {
        "room": room, "estimates": room.estimates.select_related("user"),
    })
