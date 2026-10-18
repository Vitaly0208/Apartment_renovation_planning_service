import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Room, User, Material, Estimate


def _make_room():
    return Room(1, "Гостиная", 5.5, 4.2, 2.7)


def _make_user():
    return User(1, "Иван Петров", "+79001234567", "ivan@mail.ru")


def _make_materials():
    """Создать список материалов для сметы."""
    return [
        Material(1, "Обои", "рулон", 1500.0, 5.0),
        Material(2, "Краска", "литр", 800.0, 3.0),
    ]


def test_estimate_creation():
    room = _make_room()
    user = _make_user()
    materials = _make_materials()
    estimate = Estimate(1, room, user, materials, 20000.0)
    assert estimate.id == 1
    assert estimate.room is room
    assert estimate.user is user
    assert len(estimate.materials) == 2
    # materials_cost = 1500.0 + 800.0 = 2300.0
    assert estimate.materials_cost == 2300.0
    # total = 2300.0 + 20000.0 = 22300.0
    assert estimate.total == 22300.0


def test_estimate_budget_sufficient():
    room = _make_room()
    user = _make_user()
    materials = _make_materials()
    estimate = Estimate(1, room, user, materials, 20000.0)
    # total = 22300.0
    result = estimate.check_budget(100000.0)
    assert result["is_sufficient"] is True


def test_estimate_budget_insufficient():
    room = _make_room()
    user = _make_user()
    materials = _make_materials()
    estimate = Estimate(1, room, user, materials, 20000.0)
    # total = 22300.0
    result = estimate.check_budget(1000.0)
    assert result["is_sufficient"] is False


def test_estimate_str_contains_user_and_room():
    room = _make_room()
    user = _make_user()
    materials = _make_materials()
    estimate = Estimate(1, room, user, materials, 20000.0)
    text = str(estimate)
    assert "Иван Петров" in text
    assert "Гостиная" in text
    assert "Обои" in text
    assert "Краска" in text


def test_estimate_to_data_stores_ids():
    room = _make_room()
    user = _make_user()
    materials = _make_materials()
    estimate = Estimate(1, room, user, materials, 20000.0)
    data = estimate.to_data()
    assert data["room_id"] == room.id
    assert data["user_id"] == user.id
    assert data["material_ids"] == [1, 2]
    assert data["works_cost"] == 20000.0
