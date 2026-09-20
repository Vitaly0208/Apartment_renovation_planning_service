from rooms import (
    add_room,
    calculate_room_area,
    calculate_wall_area,
    sort_rooms_by_area,
)
from materials import (
    add_material,
    calculate_quantity,
    calculate_material_cost,
)
from estimates import (
    create_estimate,
    check_budget,
    get_total_estimates,
)
from storage import load_data, save_data
from utils import input_int, input_positive_float

DATA_DIR = "data"
ROOMS_FILE = f"{DATA_DIR}/rooms.json"
MATERIALS_FILE = f"{DATA_DIR}/materials.json"
ESTIMATES_FILE = f"{DATA_DIR}/estimates.json"


def show_menu() -> None:
    """Вывести меню приложения."""
    print("\n=== Сервис планирования ремонта ===")
    print("1. Показать помещения")
    print("2. Добавить помещение")
    print("3. Показать материалы")
    print("4. Добавить материал")
    print("5. Рассчитать смету для помещения")
    print("6. Показать все сметы")
    print("7. Проверить общий бюджет")
    print("0. Выход")


def show_rooms_menu(rooms: list) -> None:
    """Показать список помещений."""
    for room in sort_rooms_by_area(rooms):
        area = calculate_room_area(room["length"], room["width"])
        print(f"  [{room['id']}] {room['name']} — {area} кв.м")


def add_room_menu(rooms: list) -> None:
    """Добавить новое помещение."""
    name = input("Название помещения: ")
    length = input_positive_float("Длина (м): ")
    width = input_positive_float("Ширина (м): ")
    height = input_positive_float("Высота (м): ")
    add_room(rooms, name, length, width, height)
    save_data(ROOMS_FILE, rooms)
    print("Помещение добавлено.")


def show_materials_menu(materials: list) -> None:
    """Показать список материалов."""
    for material in materials:
        print(
            f"  [{material['id']}] {material['name']} — "
            f"{material['price']} руб./{material['unit']}"
        )


def add_material_menu(materials: list) -> None:
    """Добавить новый материал."""
    name = input("Название материала: ")
    unit = input("Единица измерения: ")
    price = input_positive_float("Цена за единицу: ")
    coverage = input_positive_float("Покрываемая площадь: ")
    add_material(materials, name, unit, price, coverage)
    save_data(MATERIALS_FILE, materials)
    print("Материал добавлен.")


def estimate_menu(
    rooms: list,
    materials: list,
    estimates: list,
) -> None:
    """Рассчитать смету для помещения."""
    if not rooms or not materials:
        print("Сначала добавьте помещения и материалы.")
        return
    room_id = input_int("ID помещения: ")
    wall_area = 0
    room_name = ""
    for room in rooms:
        if room["id"] == room_id:
            wall_area = calculate_wall_area(
                room["length"], room["width"], room["height"],
            )
            room_name = room["name"]
            break
    if wall_area == 0:
        print("Помещение не найдено.")
        return

    materials_cost = 0
    for material in materials:
        quantity = calculate_quantity(wall_area, material["coverage"])
        cost = calculate_material_cost(quantity, material["price"])
        materials_cost += cost
        print(
            f"  {material['name']}: "
            f"{quantity} {material['unit']} = {cost} руб."
        )

    works_cost = input_positive_float("Стоимость работ: ")
    create_estimate(
        estimates, room_id, room_name, materials_cost, works_cost,
    )
    save_data(ESTIMATES_FILE, estimates)
    print(f"Смета создана. Итого материалов: {materials_cost} руб.")


def show_estimates_menu(estimates: list) -> None:
    """Показать все сметы."""
    for estimate in estimates:
        print(
            f"  [{estimate['id']}] {estimate['room_name']}: "
            f"{estimate['total']} руб."
        )


def budget_menu(estimates: list) -> None:
    """Проверить общий бюджет."""
    total = get_total_estimates(estimates)
    budget = input_positive_float("Ваш бюджет: ")
    result = check_budget(budget, total)
    print(result["message"])


def main() -> None:
    """Точка запуска приложения."""
    rooms = load_data(ROOMS_FILE)
    materials = load_data(MATERIALS_FILE)
    estimates = load_data(ESTIMATES_FILE)

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
            estimate_menu(rooms, materials, estimates)
        elif choice == 6:
            show_estimates_menu(estimates)
        elif choice == 7:
            budget_menu(estimates)
        elif choice == 0:
            print("До свидания!")
            break


if __name__ == "__main__":
    main()
