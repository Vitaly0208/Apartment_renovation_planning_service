import json
from db.database import get_connection

ROOMS_FILE = "data/rooms.json"
MATERIALS_FILE = "data/materials.json"
USERS_FILE = "data/users.json"
ESTIMATES_FILE = "data/estimates.json"


def load_json(filename):
    """Загрузить данные из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_rooms(conn):
    """Импортировать помещения."""
    rooms = load_json(ROOMS_FILE)
    conn.executemany(
        """
        INSERT INTO rooms (id, name, length, width, height)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (r["id"], r["name"], r["length"], r["width"], r["height"])
            for r in rooms
        ],
    )


def import_materials(conn):
    """Импортировать материалы."""
    materials = load_json(MATERIALS_FILE)
    conn.executemany(
        """
        INSERT INTO materials (id, name, unit, price, coverage)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (m["id"], m["name"], m["unit"], m["price"], m["coverage"])
            for m in materials
        ],
    )


def import_users(conn):
    """Импортировать пользователей."""
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (id, name, phone, email)
        VALUES (?, ?, ?, ?)
        """,
        [(u["id"], u["name"], u["phone"], u["email"]) for u in users],
    )


def import_estimates(conn):
    """Импортировать сметы."""
    estimates = load_json(ESTIMATES_FILE)

    # Загружаем все материалы один раз, чтобы искать их по ID
    all_materials = load_json(MATERIALS_FILE)
    materials_map = {m["id"]: m for m in all_materials}

    rows_to_insert = []
    for e in estimates:
        # Рассчитываем стоимость материалов на лету
        material_ids = e.get("material_ids", [])
        materials_cost = sum(
            materials_map[mid]["price"]
            for mid in material_ids
            if mid in materials_map
        )

        rows_to_insert.append((
            e["id"],
            e["room_id"],
            e["user_id"],
            round(materials_cost, 2),
            e["works_cost"],
            e["total"],
        ))

    conn.executemany(
        """
        INSERT INTO estimates (id, room_id, user_id, materials_cost, works_cost, total)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows_to_insert,
    )


def main():
    """Основная функция импорта."""
    conn = get_connection()
    try:
        import_rooms(conn)
        import_materials(conn)
        import_users(conn)
        import_estimates(conn)
        conn.commit()
        print("Данные успешно импортированы.")
    except Exception as error:
        conn.rollback()
        print(f"Ошибка импорта: {error}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
