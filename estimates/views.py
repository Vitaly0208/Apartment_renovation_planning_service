from django.shortcuts import render

from models.estimates import find_estimate_by_id
from storage import load_estimates, load_rooms, load_users, load_materials


def estimates_list(request):
    """Список смет."""
    rooms = load_rooms("data/rooms.json")
    users = load_users("data/users.json")
    materials = load_materials("data/materials.json")
    estimates_list = load_estimates(
        "data/estimates.json", rooms, users, materials,
    )
    context = {"estimates": estimates_list}
    return render(request, "estimates/estimate_list.html", context)


def estimate_detail(request, estimate_id: int):
    """Детальная страница сметы."""
    rooms = load_rooms("data/rooms.json")
    users = load_users("data/users.json")
    materials = load_materials("data/materials.json")
    estimates_list = load_estimates(
        "data/estimates.json", rooms, users, materials,
    )
    estimate = find_estimate_by_id(estimates_list, estimate_id)
    context = {"estimate": estimate}
    return render(
        request,
        "estimates/estimate_detail.html",
        context,
        status=404 if estimate is None else 200,
    )
