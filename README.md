# Сервис планирования ремонта квартиры

Консольное приложение для планирования ремонта: расчёт площадей, подбор материалов, составление смет и контроль бюджета.

## Возможности
- учёт помещений с размерами;
- каталог материалов с ценами;
- автоматический расчёт количества материалов;
- составление смет по помещениям;
- проверка бюджета;
- сохранение данных между запусками.

## Основные классы

### Room — помещение
Объект `Room` представляет помещение для ремонта.

Основные атрибуты:
- `id` — уникальный идентификатор;
- `name` — название помещения;
- `length` — длина в метрах;
- `width` — ширина в метрах;
- `height` — высота потолков в метрах.

Основные методы:
- `calculate_floor_area()` — расчёт площади пола;
- `calculate_wall_area()` — расчёт площади стен;
- `is_suitable_for()` — проверка соответствия площади;
- `__str__()` — строковое представление.

### Material — материал
Объект `Material` представляет строительный материал.

Основные атрибуты:
- `id` — уникальный идентификатор;
- `name` — название материала;
- `unit` — единица измерения;
- `price` — цена за единицу;
- `coverage` — покрываемая площадь.

Основные методы:
- `calculate_quantity()` — расчёт количества материала;
- `calculate_cost()` — расчёт стоимости;
- `__str__()` — строковое представление.

### Estimate — смета
Объект `Estimate` представляет смету ремонта помещения.

Основные атрибуты:
- `id` — уникальный идентификатор;
- `room` — объект `Room`;
- `materials_cost` — стоимость материалов;
- `works_cost` — стоимость работ;
- `total` — общая стоимость.

Основные методы:
- `check_budget()` — проверка достаточности бюджета;
- `__str__()` — строковое представление.

## Веб-интерфейс (ПР5)
Проект дополнен веб-приложением на Django 5.2.
- `/` – главная страница.
- `/rooms/` – список помещений (данные из `data/rooms.json`).
- `/rooms/<id>/` – детальная информация о помещении.
- `/estimates/` – список смет с прямым отображением объектов `Material` и `User`.
- `/estimates/<id>/` – детальная страница сметы.

### Запуск веб-версии
```bash
python manage.py runserver

## Структура проекта

```text
Apartment_renovation_planning_service/
├── main.py
├── manage.py 
├── requirements.txt 
├── README.md 
├── .gitignore 
├── .flake8 
│
├── apartment_renovation/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── homepage/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py
│
├── rooms/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py   
│
├── estimates/   
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py  
│   ├── tests.py
│   ├── views.py    
│   └── urls.py 
│
── models/      
│   ├── __init__.py    
│   ├── rooms.py 
│   ├── materials.py 
│   ├── users.py  
│   └── estimates.py 
│
├── storage.py
├── utils.py   
│
├── data/             
│   ├── rooms.json       
│   ├── materials.json 
│   ├── users.json   
│   └── estimates.json 
│
└── tests/                      
    ├── test_rooms.py            
    ├── test_materials.py 
    ├── test_users.py   
    └── test_estimates.py


