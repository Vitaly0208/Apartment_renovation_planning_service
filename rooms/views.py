from django.shortcuts import render
import sqlite3

DB_PATH = "data/renovation.sqlite"


def rooms_list(request):
    """Список помещений из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rooms = conn.execute(
        """
        SELECT id, name, length, width, height
        FROM rooms
        ORDER BY name;
        """
    ).fetchall()
    conn.close()

    context = {"rooms": rooms}
    return render(request, "rooms/room_list.html", context)


def room_detail(request, room_id: int):
    """Детальная страница помещения из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    room = conn.execute(
        """
        SELECT id, name, length, width, height,
               ROUND(length * width, 2) AS floor_area,
               ROUND(2 * (length + width) * height, 2) AS wall_area
        FROM rooms
        WHERE id = ?;
        """,
        (room_id,),
    ).fetchone()
    conn.close()

    context = {"room": room}
    status = 404 if room is None else 200
    return render(request, "rooms/room_detail.html", context, status=status)


def available_rooms(request):
    """Поиск помещений по критерию (например, площадь > N)."""
    min_area = request.GET.get("min_area")
    rooms = []
    if min_area:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rooms = conn.execute(
            """
            SELECT id, name, length, width, height,
                   ROUND(length * width, 2) AS floor_area
            FROM rooms
            WHERE (length * width) >= ?
            ORDER BY name;
            """,
            (float(min_area),),
        ).fetchall()
        conn.close()

    context = {"rooms": rooms, "min_area": min_area}
    return render(request, "rooms/available.html", context)
