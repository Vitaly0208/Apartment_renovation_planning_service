from typing import List
from models import Room, Material, User, Estimate
from storage import (
    load_rooms, save_rooms,
    load_materials, save_materials,
    load_users, save_users,
    load_estimates, save_estimates,
)
from utils import input_int, input_positive_float

DATA_DIR = "data"
ROOMS_FILE = f"{DATA_DIR}/rooms.json"
MATERIALS_FILE = f"{DATA_DIR}/materials.json"
USERS_FILE = f"{DATA_DIR}/users.json"
ESTIMATES_FILE = f"{DATA_DIR}/estimates.json"


def show_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Сервис планирования ремонта ===")
    print("1. Показать помещения")
    print("2. Добавить помещение")
    print("3. Показать материалы")
    print("4. Добавить материал")
    print("5. Показать пользователей")
    print("6. Добавить пользователя")
    print("7. Рассчитать смету для помещения")
    print("8. Показать все сметы")
    print("9. Показать сметы пользователя")
    print("10. Проверить общий бюджет")
    print("0. Выход")


def show_rooms_menu(rooms: List[Room]) -> None:
    """Показать список помещений."""
    sorted_rooms = sorted(rooms, key=lambda r: r.calculate_floor_area())
    for room in sorted_rooms:
        print(room)


def add_room_menu(rooms: List[Room]) -> None:
    """Добавить новое помещение."""
    name = input("Название помещения: ")
    length = input_positive_float("Длина (м): ")
    width = input_positive_float("Ширина (м): ")
    height = input_positive_float("Высота (м): ")
    room_id = max((r.id for r in rooms), default=0) + 1
    room = Room(room_id, name, length, width, height)
    rooms.append(room)
    save_rooms(ROOMS_FILE, rooms)
    print(f"Помещение добавлено: {room}")


def show_materials_menu(materials: List[Material]) -> None:
    """Показать список материалов."""
    for material in materials:
        print(material)


def add_material_menu(materials: List[Material]) -> None:
    """Добавить новый материал."""
    name = input("Название материала: ")
    unit = input("Единица измерения: ")
    price = input_positive_float("Цена за единицу: ")
    coverage = input_positive_float("Покрываемая площадь: ")
    material_id = max((m.id for m in materials), default=0) + 1
    material = Material(material_id, name, unit, price, coverage)
    materials.append(material)
    save_materials(MATERIALS_FILE, materials)
    print(f"Материал добавлен: {material}")


def show_users_menu(users: List[User]) -> None:
    """Показать список пользователей."""
    for user in users:
        print(user)


def add_user_menu(users: List[User]) -> None:
    """Добавить нового пользователя."""
    name = input("Имя пользователя: ")
    phone = input("Телефон: ")
    email = input("Email: ")
    user_id = max((u.id for u in users), default=0) + 1
    user = User(user_id, name, phone, email)
    users.append(user)
    save_users(USERS_FILE, users)
    print(f"Пользователь добавлен: {user}")


def estimate_menu(
    rooms: List[Room],
    materials: List[Material],
    users: List[User],
    estimates: List[Estimate],
) -> None:
    """Рассчитать смету для помещения."""
    if not rooms or not materials or not users:
        print("Сначала добавьте помещения, материалы и пользователей.")
        return

    user_id = input_int("ID пользователя: ")
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        print("Пользователь не найден.")
        return

    room_id = input_int("ID помещения: ")
    room = next((r for r in rooms if r.id == room_id), None)
    if not room:
        print("Помещение не найдено.")
        return

    wall_area = room.calculate_wall_area()
    materials_cost = 0
    for material in materials:
        quantity = material.calculate_quantity(wall_area)
        cost = material.calculate_cost(quantity)
        materials_cost += cost
        print(
            f"  {material.name}: "
            f"{quantity} {material.unit} = {cost} руб."
        )

    works_cost = input_positive_float("Стоимость работ: ")
    estimate_id = max((e.id for e in estimates), default=0) + 1
    estimate = Estimate(
        estimate_id, room, user, materials_cost, works_cost,
    )
    estimates.append(estimate)
    save_estimates(ESTIMATES_FILE, estimates)
    print(f"Смета создана: {estimate}")


def show_estimates_menu(estimates: List[Estimate]) -> None:
    """Показать все сметы."""
    for estimate in estimates:
        print(estimate)


def show_user_estimates_menu(
    users: List[User],
    estimates: List[Estimate],
) -> None:
    """Показать сметы конкретного пользователя."""
    if not users:
        print("Сначала добавьте пользователей.")
        return
    user_id = input_int("ID пользователя: ")
    user = next((u for u in users if u.id == user_id), None)
    if not user:
        print("Пользователь не найден.")
        return

    user_estimates = [e for e in estimates if e.user.id == user_id]
    if not user_estimates:
        print(f"У пользователя {user.name} нет смет.")
        return

    print(f"\nСметы пользователя {user.name}:")
    total = 0
    for estimate in user_estimates:
        print(estimate)
        total += estimate.total
    print(f"Общая сумма: {round(total, 2)} руб.")


def budget_menu(estimates: List[Estimate]) -> None:
    """Проверить общий бюджет."""
    total = sum(e.total for e in estimates)
    budget = input_positive_float("Ваш бюджет: ")
    if budget >= total:
        print(f"Бюджет достаточен. Остаток: {round(budget - total, 2)} руб.")
    else:
        print(f"Недостаточно средств. Не хватает: {round(total - budget, 2)} руб.")


def main() -> None:
    """Точка запуска приложения."""
    rooms = load_rooms(ROOMS_FILE)
    materials = load_materials(MATERIALS_FILE)
    users = load_users(USERS_FILE)
    estimates = load_estimates(ESTIMATES_FILE, rooms, users)

    while True:
        show_menu()
        choice = input_int("Выберите действие: ")

        if choice == 1:
            show_rooms_menu(rooms)
        elif choice == 2:
            add_room_menu(rooms)
        elif choice == 3:
            show_materials_menu(materials)
        elif choice == 4:
            add_material_menu(materials)
        elif choice == 5:
            show_users_menu(users)
        elif choice == 6:
            add_user_menu(users)
        elif choice == 7:
            estimate_menu(rooms, materials, users, estimates)
        elif choice == 8:
            show_estimates_menu(estimates)
        elif choice == 9:
            show_user_estimates_menu(users, estimates)
        elif choice == 10:
            budget_menu(estimates)
        elif choice == 0:
            print("До свидания!")
            break


if __name__ == "__main__":
    main()
