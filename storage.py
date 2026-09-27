import json
import os
from typing import List
from models import Room, Material, Estimate


def load_rooms(filename: str) -> List[Room]:
    """Загрузить помещения из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [Room.from_data(item) for item in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Ошибка чтения JSON: {error}")
        return []


def save_rooms(filename: str, rooms: List[Room]) -> None:
    """Сохранить помещения в JSON-файл."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = [room.to_data() for room in rooms]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_materials(filename: str) -> List[Material]:
    """Загрузить материалы из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            return [Material.from_data(item) for item in data]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Ошибка чтения JSON: {error}")
        return []


def save_materials(filename: str, materials: List[Material]) -> None:
    """Сохранить материалы в JSON-файл."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = [material.to_data() for material in materials]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_estimates(filename: str, rooms: List[Room]) -> List[Estimate]:
    """Загрузить сметы из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            estimates = []
            for item in data:
                room = next((r for r in rooms if r.id == item["room_id"]), None)
                if room:
                    estimates.append(Estimate.from_data(item, room))
            return estimates
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        print(f"Ошибка чтения JSON: {error}")
        return []


def save_estimates(filename: str, estimates: List[Estimate]) -> None:
    """Сохранить сметы в JSON-файл."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data = [estimate.to_data() for estimate in estimates]
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
