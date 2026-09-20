import math


def add_material(
    materials: list[dict],
    name: str,
    unit: str,
    price: float,
    coverage: float,
) -> None:
    """Добавить материал в каталог."""
    material_id = max((m["id"] for m in materials), default=0) + 1
    materials.append({
        "id": material_id,
        "name": name,
        "unit": unit,
        "price": price,
        "coverage": coverage,
    })


def find_material(materials: list[dict], query: str) -> list[dict]:
    """Найти материалы по подстроке названия."""
    query_lower = query.lower()
    return [
        m for m in materials if query_lower in m["name"].lower()
    ]


def calculate_quantity(area: float, coverage: float) -> int:
    """Рассчитать количество единиц материала."""
    return math.ceil(area / coverage)


def calculate_material_cost(quantity: int, price: float) -> float:
    """Рассчитать стоимость материала."""
    return round(quantity * price, 2)
