import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import User


def test_user_creation():
    user = User(1, "Иван Петров", "+79001234567", "ivan@mail.ru")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.phone == "+79001234567"
    assert user.email == "ivan@mail.ru"


def test_user_str():
    user = User(1, "Иван Петров", "+79001234567", "ivan@mail.ru")
    text = str(user)
    assert "Иван Петров" in text
    assert "+79001234567" in text


def test_user_to_data_and_back():
    user = User(1, "Иван Петров", "+79001234567", "ivan@mail.ru")
    data = user.to_data()
    restored = User.from_data(data)
    assert restored.id == user.id
    assert restored.name == user.name
    assert restored.phone == user.phone
    assert restored.email == user.email
    
