def create_estimate(
    estimates: list[dict],
    room_id: int,
    room_name: str,
    materials_cost: float,
    works_cost: float,
) -> None:
    """Создать смету для помещения."""
    estimate_id = max((e["id"] for e in estimates), default=0) + 1
    total = round(materials_cost + works_cost, 2)
    estimates.append({
        "id": estimate_id,
        "room_id": room_id,
        "room_name": room_name,
        "materials_cost": materials_cost,
        "works_cost": works_cost,
        "total": total,
    })


def check_budget(budget: float, total_cost: float) -> dict:
    """Проверить достаточность бюджета."""
    if budget >= total_cost:
        return {
            "is_sufficient": True,
            "message": (
                f"Бюджет достаточен. "
                f"Остаток: {round(budget - total_cost, 2)} руб."
            ),
        }
    return {
        "is_sufficient": False,
        "message": (
            f"Недостаточно средств. "
            f"Не хватает: {round(total_cost - budget, 2)} руб."
        ),
    }


def get_total_estimates(estimates: list[dict]) -> float:
    """Рассчитать общую стоимость всех смет."""
    return round(sum(e["total"] for e in estimates), 2)
