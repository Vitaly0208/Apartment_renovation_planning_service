import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Room, Estimate


def test_estimate_creation():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    estimate = Estimate(1, room, 30000.0, 20000.0)
    assert estimate.id == 1
    assert estimate.room is room
    assert estimate.total == 50000.0


def test_estimate_budget_sufficient():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    estimate = Estimate(1, room, 30000.0, 20000.0)
    result = estimate.check_budget(100000.0)
    assert result["is_sufficient"] is True


def test_estimate_budget_insufficient():
    room = Room(1, "Гостиная", 5.5, 4.2, 2.7)
    estimate = Estimate(1, room, 30000.0, 20000.0)
    result = estimate.check_budget(30000.0)
    assert result["is_sufficient"] is False
