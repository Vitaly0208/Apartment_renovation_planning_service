from typing import Optional


def add_room(
    rooms: list[dict],
    name: str,
    length: float,
    width: float,
    height: float,
) -> None:
    room_id = max((room["id"] for room in rooms), default=0) + 1
    rooms.append({
        "id": room_id,
        "name": name,
        "length": length,
        "width": width,
        "height": height,
    })


def find_room(rooms: list[dict], query: str) -> list[dict]:
    query_lower = query.lower()
    return [room for room in rooms if query_lower in room["name"].lower()]


def calculate_room_area(length: float, width: float) -> float:
    return round(length * width, 2)


def calculate_wall_area(
    length: float,
    width: float,
    height: float,
) -> float:
    perimeter = 2 * (length + width)
    return round(perimeter * height, 2)


def get_room_by_id(rooms: list[dict], room_id: int) -> Optional[dict]:
    for room in rooms:
        if room["id"] == room_id:
            return room
    return None


def sort_rooms_by_area(rooms: list[dict]) -> list[dict]:
    return sorted(rooms, key=lambda r: r["length"] * r["width"])
