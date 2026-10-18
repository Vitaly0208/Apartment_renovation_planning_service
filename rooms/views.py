from django.http import HttpResponse

from homepage.views import page
from storage import load_rooms
from models.rooms import find_room_by_id


def rooms_list(request):
    """Список помещений."""
    rooms_data = load_rooms("data/rooms.json")
    items = "".join(
        [
            "<li class=\"list-group-item\">"
            f"{room.name} – {room.calculate_floor_area()} кв.м"
            "</li>"
            for room in rooms_data
        ]
    )
    content = f"<h1>Помещения</h1><ul class='list-group'>{items}</ul>"
    return HttpResponse(page("Помещения", content))


def room_detail(request, room_id: int):
    """Детальная страница помещения."""
    rooms_data = load_rooms("data/rooms.json")
    room = find_room_by_id(rooms_data, room_id)

    if room is None:
        content = (
            "<h1 class='text-danger'>Помещение не найдено</h1>"
            "<a href='/rooms/' class='btn btn-outline-secondary'>"
            "← Назад</a>"
        )
        return HttpResponse(page("Не найдено", content), status=404)

    content = (
        "<div class=\"card\">\n"
        "  <div class=\"card-body\">\n"
        f"    <h5 class=\"card-title\">{room.name}</h5>\n"
        "    <p class=\"card-text\"><strong>Площадь:</strong> "
        f"{room.calculate_floor_area()} кв.м</p>\n"
        "    <p class=\"card-text\"><strong>Площадь стен:</strong> "
        f"{room.calculate_wall_area()} кв.м</p>\n"
        "    <a href=\"/rooms/\" class=\"btn btn-outline-secondary\">"
        "← Назад</a>\n"
        "  </div>\n"
        "</div>\n"
    )
    return HttpResponse(page(room.name, content), status=200)
