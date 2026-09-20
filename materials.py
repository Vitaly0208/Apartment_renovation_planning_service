import math


def add_material(
    materials: list[dict],
    name: str,
    unit: str,
    price: float,
    coverage: float,
) -> None:
    material_id = max((m["id"] for m in materials), default=0) + 1
    materials.append({
        "id": material_id,
        "name": name,
        "unit": unit,
        "price": price,
        "coverage": coverage,
    })


def find_material(materials: list[dict], query: str) -> list[dict]:
    query_lower = query.lower()
    return [
        m for m in materials if query_lower in m["name"].lower()
    ]


def calculate_quantity(area: float, coverage: float) -> int:
    return math.ceil(area / coverage)


def calculate_material_cost(quantity: int, price: float) -> float:
    return round(quantity * price, 2)
