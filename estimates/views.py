from django.http import HttpResponse

from homepage.views import page
from storage import (
    load_estimates,
    load_rooms,
    load_users,
    load_materials,
)


def estimates_list(request):
    """Список смет."""
    rooms = load_rooms("data/rooms.json")
    users = load_users("data/users.json")
    materials = load_materials("data/materials.json")
    estimates_data = load_estimates(
        "data/estimates.json", rooms, users, materials,
    )

    items = "".join(
        [
            "<li class=\"list-group-item d-flex "
            "justify-content-between align-items-center\">"
            f"<a href=\"/estimates/{estimate.id}/\">"
            f"{estimate.user.name} → {estimate.room.name}</a>"
            "<span class=\"badge bg-primary rounded-pill\">"
            f"{estimate.total} руб.</span>"
            "</li>"
            for estimate in estimates_data
        ]
    )
    if items:
        content = f"<h1>Сметы</h1><ul class='list-group'>{items}</ul>"
    else:
        content = "<h1>Сметы</h1><p>Смет пока нет.</p>"
    return HttpResponse(page("Сметы", content))


def estimate_detail(request, estimate_id: int):
    """Детальная страница сметы."""
    rooms = load_rooms("data/rooms.json")
    users = load_users("data/users.json")
    materials = load_materials("data/materials.json")
    estimates_data = load_estimates(
        "data/estimates.json", rooms, users, materials,
    )

    estimate = next(
        (e for e in estimates_data if e.id == estimate_id), None,
    )

    if estimate is None:
        content = (
            "<h1 class='text-danger'>Смета не найдена</h1>"
            "<a href='/estimates/' class='btn btn-outline-secondary'>"
            "← Назад</a>"
        )
        return HttpResponse(page("Не найдено", content), status=404)

    materials_list = "<br>".join(
        [f"• {m.name}" for m in estimate.materials],
    )
    content = (
        "<div class=\"card\">\n"
        "  <div class=\"card-body\">\n"
        f"    <h5 class=\"card-title\">Смета №{estimate.id}</h5>\n"
        "    <p class=\"card-text\"><strong>Заказчик:</strong> "
        f"{estimate.user.name}</p>\n"
        "    <p class=\"card-text\"><strong>Помещение:</strong> "
        f"{estimate.room.name}</p>\n"
        "    <p class=\"card-text\"><strong>Материалы:</strong><br>"
        f"{materials_list}</p>\n"
        "    <p class=\"card-text\"><strong>Стоимость работ:</strong> "
        f"{estimate.works_cost} руб.</p>\n"
        f"    <h4 class=\"text-success\">Итого: "
        f"{estimate.total} руб.</h4>\n"
        "    <a href=\"/estimates/\" class=\"btn btn-outline-secondary\">"
        "← Назад</a>\n"
        "  </div>\n"
        "</div>\n"
    )
    return HttpResponse(page(f"Смета №{estimate.id}", content), status=200)
