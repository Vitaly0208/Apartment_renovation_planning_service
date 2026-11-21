# Сервис планирования ремонта квартиры

Автор: Шелоумов В.К., ЭФБО-03-24, РТУ МИРЭА.
Дисциплина: «Технологии разработки приложений на базе фреймворков».

Консольное приложение ПР1–ПР4 и веб-приложение Django ПР5–ПР9:
помещения, каталог материалов, заказчики, сметы и контроль бюджета.
Технологии: Python, Django 5.2, SQLite, Django ORM, pytest, flake8.

## Запуск

```powershell
git clone https://github.com/Vitaly0208/Apartment_renovation_planning_service
cd Apartment_renovation_planning_service
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py import_pr7
python manage.py runserver
```

Открыть http://127.0.0.1:8000/. Консольная версия: `python main.py`.
Для админки: `python manage.py createsuperuser`, затем `/admin/`.

## Страницы

| URL | Возможности |
| --- | --- |
| `/` | Главная страница |
| `/rooms/` | Помещения, поиск по названию, фильтр площади, сортировка |
| `/rooms/<id>/` | Размеры, площади пола и стен, связанные сметы |
| `/rooms/available/` | Поиск по минимальной площади и названию |
| `/estimates/` | Сметы, поиск по помещению/заказчику/email, фильтры и сортировка |
| `/estimates/<id>/` | Помещение, контакты заказчика, материалы и суммы |
| `/estimates/statistics/` | Общие показатели, статистика заказчиков, помещений и материалов |

Фильтры смет: `room`, `user`, `min_total`, `max_total`, `paid_only`, `q`.
Сортировка `sort`: `id`, `total`, `-total`, `room`, `user`.
Пагинация: по 5 смет, параметр `page`; ссылки сохраняют все GET-параметры
через встроенный тег `{% querystring %}`. Нечисловая страница открывает первую,
номер вне диапазона — последнюю. Ошибки фильтров отображаются возле полей,
выборка при ошибке пустая. Отсутствующая карточка возвращает HTTP 404.
Пример: `/estimates/?min_total=100&sort=-total&page=1`.

Поиск площади заменяет пример поиска свободных комнат Roomly: в предметной
области ремонта нет бронирований, дат занятости и статусов отмены.

## Модели и связи ПР9

| Модель | Поля |
| --- | --- |
| `rooms.Room` | id, name, length, width, height |
| `estimates.User` | id, name, phone, email |
| `estimates.Material` | id, name, unit, price, coverage |
| `estimates.Estimate` | id, room, user, materials, materials_cost, works_cost, total |

Первичные ключи — автоматически создаваемые BigAutoField. Размеры, цены и суммы
хранятся в DecimalField. Размеры и покрытие положительны, суммы неотрицательны;
ограничения проверяются валидаторами и CHECK в БД. Total равен сумме двух затрат.
Числовые значения затрат по умолчанию равны нулю, прочие основные поля обязательны.
User — заказчик, отдельный от встроенного пользователя авторизации Django.

Estimate.room и Estimate.user — ForeignKey с `on_delete=PROTECT`,
`related_name="estimates"`: помещение/заказчика нельзя удалить, пока есть сметы.
Estimate.materials — ManyToManyField с обратным именем `estimates`, восстанавливающий
состав материалов консольной версии. Каталог и заказчики размещены в существующем
приложении estimates. Расчёт площадей и методы расчёта материалов сохранены.
Суммы сметы — сохранённый расчёт: изменение цены каталога не меняет старые сметы;
при ручном изменении затрат необходимо согласованно обновить total.

## Переход с ПР7 и данные

ПР7 использовала `data/renovation.sqlite` и ручные SQL-запросы в views.py.
ПР9 использует **`db.sqlite3`**, определённую через BASE_DIR в settings.py.
Миграции `rooms/0001_initial` и `estimates/0001_initial` создают новые таблицы.
Исходная база и JSON сохранены. Ранее отслеживаемый db.sqlite3 остаётся локальным
артефактом исходного репозитория; новые локальные базы исключаются .gitignore.
Развёртывание не зависит от наличия готовой базы: достаточно migrate и import_pr7.

```powershell
python manage.py import_pr7
python manage.py import_pr7 --source data/renovation.sqlite --materials-json data/estimates.json
```

Импортер читает старую SQLite в режиме read-only, переносит четыре таблицы через
ORM в транзакции, сохраняет id и внешние ключи. Состав материалов, отсутствующий
в схеме ПР7, берётся из material_ids в data/estimates.json. Суммы из SQLite
не пересчитываются. Повторный импорт идентичных данных безопасен; при конфликте
с уже изменёнными записями операция полностью откатывается, ничего не перезаписывая.
При отсутствии JSON выводится предупреждение; сметы без состава допустимы.
Старый email `vas@ru` сохраняется как исходное значение; новые адреса должны проходить
валидацию EmailField (например, через админку).

Контроль исходных данных: 3 помещения, 1 заказчик, 2 материала, 1 смета.
Смета №1: room_id=1, user_id=1, материалы 1 и 2, затраты 200+500=700 руб.
Прямой sqlite3 остался только в историческом db/ и в импортере для чтения источника.
Веб-представления не используют SQL, JSON или старые load_*.

Fixture можно выгрузить и загрузить в пустую совместимую базу после migrate:

```powershell
python -X utf8 manage.py dumpdata rooms estimates --indent 2 --output data/pr9_fixture.json
python manage.py loaddata data/pr9_fixture.json
```

## ORM-запросы для защиты

Ниже перечислены отдельные выражения из работающих представлений; последовательные
условия фильтрации допускается комбинировать в одном HTTP-запросе.

| № | Операция | Место использования |
| --- | --- | --- |
| 1 | Room.objects.all() | rooms/views.py, список |
| 2 | get_object_or_404(Room, pk=...) | карточка помещения |
| 3 | filter(name__icontains=...) | поиск названия |
| 4 | alias(area=F(...)*F(...)).filter(area__gte=...) | поиск площади |
| 5 | order_by(name, pk) или выражением площади | сортировка помещений |
| 6 | room.estimates.select_related(user) | обратная связь в карточке |
| 7 | Estimate.objects.all() | список смет |
| 8 | filter(room=...) | сметы помещения |
| 9 | filter(user=...) | сметы заказчика |
| 10 | filter(total__gte=...) | нижняя граница |
| 11 | filter(total__lte=...) | верхняя граница; совместно с №10 два условия |
| 12 | exclude(total=0) | исключение бесплатных смет |
| 13 | filter(Q(room__name...) \| Q(user__name...) \| Q(user__email...)) | поиск по связям |
| 14 | order_by(поле из белого списка, pk) | сортировка смет, в том числе по связям |
| 15 | values(...).annotate(room_name=F(...), user_name=F(...)) | сокращённый список |
| 16 | select_related(room, user).prefetch_related(materials) и 404 | карточка сметы |
| 17 | User.objects.annotate(Count, Sum, Avg) | статистика заказчиков, включая без смет |
| 18 | Estimate.objects.aggregate(Count, Sum, Avg, Min, Max) | общая статистика |
| 19 | Room.objects.annotate(Count, Sum) | статистика помещений |
| 20 | Material.objects.annotate(Count) | использование каталога |
| 21 | Paginator(queryset, 5).get_page(...) | ограниченная выборка страницы |

Валидация GET-параметров — Django Forms. Название поля order_by выбирается только
из фиксированного словаря. select_related в карточке исключает N+1; values в списке
сразу получает поля связанных таблиц. Тест проверяет карточку за 2 SQL-запроса
(основной JOIN и prefetch материалов). CRUD продемонстрирован в tests/test_orm.py
на тестовых данных; создание и изменение доступны также в админке.

## Проверки

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py showmigrations
python manage.py sqlmigrate estimates 0001
python -m pytest -v
python -m flake8 . --extend-exclude=venv
```

Тестовая база создаётся отдельно, исходные данные не изменяются. В тестах проверены
CRUD, ограничения, связи, HTTP 404, некорректные параметры, поиск, сортировка,
пагинация, статистика, повторяемость импорта и полный откат при конфликте.
Длина автоматически сгенерированных миграций исключена из E501.

## Структура и предыдущие работы

- `rooms/` — модель, миграция, формы, представления и шаблоны помещений.
- `estimates/` — модели заказчика, материала и сметы; страницы, импорт, миграции.
- `homepage/`, `templates/` — главная, общая разметка и навигация.
- `models/`, `main.py`, `storage.py`, `utils.py` — исходная консольная версия.
- `db/`, `sql/`, `data/` — сохранённые результаты ПР7 и исходные данные.
- `tests/` — прежние тесты и интеграционные проверки ORM.
- `PR9_report.txt` — отчёт по работе.

Раздел «Базы данных и Django ORM» Яндекс Практикума пройден со слов автора.
Номер варианта не указан; предметная область — планирование ремонта квартиры.
