import json
import os
from typing import List
from models import Room, Material, User, Estimate


def _ensure_dir(filename: str) -> None:
    """Убедиться, что папка для файла существует."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)


def _load_json(filename: str) -> list:
    """Загрузить данные из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Ошибка чтения JSON: {error}")
        return []


def _save_json(filename: str, data: list) -> None:
    """Сохранить данные в JSON-файл."""
    _ensure_dir(filename)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_rooms(filename: str) -> List[Room]:
    """Загрузить помещения из JSON-файла."""
    data = _load_json(filename)
    return [Room.from_data(item) for item in data]


def save_rooms(filename: str, rooms: List[Room]) -> None:
    """Сохранить помещения в JSON-файл."""
    _save_json(filename, [room.to_data() for room in rooms])


def load_materials(filename: str) -> List[Material]:
    """Загрузить материалы из JSON-файла."""
    data = _load_json(filename)
    return [Material.from_data(item) for item in data]


def save_materials(filename: str, materials: List[Material]) -> None:
    """Сохранить материалы в JSON-файл."""
    _save_json(filename, [m.to_data() for m in materials])


def load_users(filename: str) -> List[User]:
    """Загрузить пользователей из JSON-файла."""
    data = _load_json(filename)
    return [User.from_data(item) for item in data]


def save_users(filename: str, users: List[User]) -> None:
    """Сохранить пользователей в JSON-файл."""
    _save_json(filename, [user.to_data() for user in users])


def load_estimates(
    filename: str,
    rooms: List[Room],
    users: List[User],
) -> List[Estimate]:
    """Загрузить сметы из JSON-файла."""
    data = _load_json(filename)
    estimates = []
    for item in data:
        room = next((r for r in rooms if r.id == item["room_id"]), None)
        user = next((u for u in users if u.id == item["user_id"]), None)
        if room and user:
            estimates.append(Estimate.from_data(item, room, user))
    return estimates


def save_estimates(filename: str, estimates: List[Estimate]) -> None:
    """Сохранить сметы в JSON-файл."""
    _save_json(filename, [e.to_data() for e in estimates])
