import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rooms import (
    add_room,
    find_room,
    calculate_room_area,
    calculate_wall_area,
)


def test_add_room():
    rooms = []
    add_room(rooms, "Гостиная", 5.5, 4.2, 2.7)
    assert len(rooms) == 1
    assert rooms[0]["name"] == "Гостиная"


def test_find_room():
    rooms = []
    add_room(rooms, "Гостиная", 5.5, 4.2, 2.7)
    add_room(rooms, "Спальня", 4.0, 3.5, 2.7)
    found = find_room(rooms, "гостин")
    assert len(found) == 1
    assert found[0]["name"] == "Гостиная"


def test_calculate_room_area():
    assert calculate_room_area(5.5, 4.2) == 23.1


def test_calculate_wall_area():
    assert calculate_wall_area(5.5, 4.2, 2.7) == 52.38
