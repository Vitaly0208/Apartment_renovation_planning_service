from datetime import datetime
import math

room_name = "Гостиная"
room_length = 5.5
room_width = 4.2
wall_height = 2.7

wallpaper_price_per_roll = 1500.0
paint_price_per_liter = 800.0
laminate_price_per_sqm = 650.0

work_price_per_sqm = 450.0

user_budget = 150000.0


def calculate_room_area(length, width):
    area = length * width
    return round(area, 2)


def calculate_wall_area(length, width, height):
    perimeter = 2 * (length + width)
    wall_area = perimeter * height
    return round(wall_area, 2)


def calculate_wallpaper_rolls(wall_area, roll_coverage=5.0):
    rolls_needed = wall_area / roll_coverage
    rolls_count = math.ceil(rolls_needed)
    return rolls_count


def calculate_materials_cost(wallpaper_rolls, wallpaper_price, floor_area, floor_price):
    wallpaper_cost = wallpaper_rolls * wallpaper_price
    floor_cost = floor_area * floor_price
    total_materials = wallpaper_cost + floor_cost
    return round(total_materials, 2)


def calculate_works_cost(floor_area, work_price):
    total_works = floor_area * work_price
    return round(total_works, 2)


def check_budget(budget, total_cost):
    if budget >= total_cost:
        remaining = budget - total_cost
        return f"✓ Бюджет достаточен. Остаток: {round(remaining, 2)} руб."
    else:
        shortage = total_cost - budget
        return f"✗ Недостаточно средств. Не хватает: {round(shortage, 2)} руб."


def print_repair_report(room, area, wall_area, rolls, materials_cost, works_cost, total_cost, budget_status):
    current_date = datetime.now().strftime("%d.%m.%Y %H:%M")

    print("=" * 50)
    print("ОТЧЕТ О ПЛАНИРОВАНИИ РЕМОНТА")
    print("=" * 50)
    print(f"Дата расчета: {current_date}")
    print(f"Помещение: {room}")
    print(f"Площадь пола: {area} кв.м")
    print(f"Площадь стен: {wall_area} кв.м")
    print("-" * 50)
    print("МАТЕРИАЛЫ:")
    print(f"  Обои: {rolls} рулонов")
    print(f"  Стоимость материалов: {materials_cost} руб.")
    print("-" * 50)
    print("РАБОТЫ:")
    print(f"  Стоимость работ: {works_cost} руб.")
    print("-" * 50)
    print(f"ИТОГО: {total_cost} руб.")
    print("-" * 50)
    print(f"Статус бюджета: {budget_status}")
    print("=" * 50)


if __name__ == "__main__":
    print(f"Начало планирования ремонта: {room_name}")
    print()

    floor_area = calculate_room_area(room_length, room_width)
    wall_area = calculate_wall_area(room_length, room_width, wall_height)

    print(f"Рассчитанная площадь пола: {floor_area} кв.м")
    print(f"Рассчитанная площадь стен: {wall_area} кв.м")
    print()

    wallpaper_rolls = calculate_wallpaper_rolls(wall_area)
    materials_cost = calculate_materials_cost(
        wallpaper_rolls,
        wallpaper_price_per_roll,
        floor_area,
        laminate_price_per_sqm
    )

    print(f"Необходимо рулонов обоев: {wallpaper_rolls}")
    print(f"Стоимость материалов: {materials_cost} руб.")
    print()

    works_cost = calculate_works_cost(floor_area, work_price_per_sqm)
    print(f"Стоимость работ: {works_cost} руб.")
    print()

    total_cost = materials_cost + works_cost
    print(f"Общая стоимость ремонта: {total_cost} руб.")
    print()

    budget_status = check_budget(user_budget, total_cost)
    print(budget_status)
    print()

    print_repair_report(
        room_name,
        floor_area,
        wall_area,
        wallpaper_rolls,
        materials_cost,
        works_cost,
        total_cost,
        budget_status
    )