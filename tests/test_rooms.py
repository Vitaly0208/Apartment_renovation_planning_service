import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Room


def test_room_creation():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    assert room.id == 1
    assert room.name == "Гостиная"
    assert room.length == 5.5


def test_room_floor_area():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    assert room.calculate_floor_area() == 23.1


def test_room_wall_area():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    assert room.calculate_wall_area() == 52.38


def test_room_str():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    assert "Гостиная" in str(room)
    assert "23.1" in str(room)
