-- ==========================================
-- Сервис планирования ремонта: структура БД
-- ==========================================

CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    length REAL NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    unit TEXT NOT NULL,
    price REAL NOT NULL,
    coverage REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS estimates (
    id INTEGER PRIMARY KEY,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    materials_cost REAL NOT NULL,
    works_cost REAL NOT NULL,
    total REAL NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);