-- Получение списка всех помещений
SELECT id, name, length, width, height
FROM rooms
ORDER BY name;

-- Помещения с площадью пола больше заданной
SELECT id, name, (length * width) AS floor_area
FROM rooms
WHERE (length * width) >= 20.0
ORDER BY floor_area DESC;

-- Все сметы с суммой больше заданной
SELECT id, room_id, user_id, total
FROM estimates
WHERE total > 50000.0
ORDER BY total DESC;

-- Полная информация о смете: помещение + пользователь + смета
SELECT
    e.id AS estimate_id,
    e.materials_cost,
    e.works_cost,
    e.total,
    r.name AS room_name,
    r.length,
    r.width,
    r.height,
    u.name AS user_name,
    u.phone,
    u.email
FROM estimates e
JOIN rooms r ON e.room_id = r.id
JOIN users u ON e.user_id = u.id
ORDER BY e.id;

-- Топ-5 самых дорогих материалов
SELECT id, name, unit, price
FROM materials
ORDER BY price DESC
LIMIT 5;

-- Общее количество смет
SELECT COUNT(*) AS estimates_count
FROM estimates;

-- Суммарная стоимость всех смет
SELECT SUM(total) AS grand_total
FROM estimates;

-- Количество смет каждого пользователя
SELECT
    u.name AS user_name,
    COUNT(e.id) AS estimates_count,
    ROUND(SUM(e.total), 2) AS total_spent
FROM users u
LEFT JOIN estimates e ON u.id = e.user_id
GROUP BY u.id, u.name
ORDER BY total_spent DESC;

-- Средняя стоимость смет по каждому помещению
SELECT
    r.name AS room_name,
    ROUND(AVG(e.total), 2) AS avg_cost,
    COUNT(e.id) AS estimate_count
FROM rooms r
LEFT JOIN estimates e ON r.id = e.room_id
GROUP BY r.id, r.name
ORDER BY avg_cost DESC;

-- Пользователи, потратившие более 100000 руб.
SELECT
    u.name AS user_name,
    COUNT(e.id) AS estimates_count,
    ROUND(SUM(e.total), 2) AS total_spent
FROM users u
JOIN estimates e ON u.id = e.user_id
GROUP BY u.id, u.name
HAVING SUM(e.total) > 100000.0
ORDER BY total_spent DESC;

