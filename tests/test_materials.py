import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from materials import (
    add_material,
    calculate_quantity,
    calculate_material_cost,
)


def test_add_material():
    materials = []
    add_material(materials, "Обои", "рулон", 1500.0, 5.0)
    assert len(materials) == 1
    assert materials[0]["name"] == "Обои"


def test_calculate_quantity():
    assert calculate_quantity(12.0, 5.0) == 3
    assert calculate_quantity(10.0, 5.0) == 2


def test_calculate_material_cost():
    assert calculate_material_cost(3, 1500.0) == 4500.0
