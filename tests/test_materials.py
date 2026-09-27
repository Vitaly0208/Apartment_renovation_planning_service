import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Material


def test_material_creation():
    material = Material(1, "Обои", "рулон", 1500.0, 5.0)
    assert material.id == 1
    assert material.name == "Обои"


def test_material_quantity():
    material = Material(1, "Обои", "рулон", 1500.0, 5.0)
    assert material.calculate_quantity(12.0) == 3


def test_material_cost():
    material = Material(1, "Обои", "рулон", 1500.0, 5.0)
    assert material.calculate_cost(3) == 4500.0
