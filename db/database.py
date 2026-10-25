import sqlite3

DB_PATH = "data/renovation.sqlite"


def get_connection():
    """Создать соединение с базой данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
