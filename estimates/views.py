import sqlite3
from django.shortcuts import render

DB_PATH = "data/renovation.sqlite"


def estimates_list(request):
    """Список смет из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    estimates = conn.execute(
        """
        SELECT
            e.id,
            e.materials_cost,
            e.works_cost,
            e.total,
            r.name AS room_name,
            u.name AS user_name
        FROM estimates e
        JOIN rooms r ON e.room_id = r.id
        JOIN users u ON e.user_id = u.id
        ORDER BY e.id;
        """
    ).fetchall()
    conn.close()

    context = {"estimates": estimates}
    return render(request, "estimates/estimate_list.html", context)


def estimate_detail(request, estimate_id: int):
    """Детальная страница сметы из базы данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    estimate = conn.execute(
        """
        SELECT
            e.id,
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
        WHERE e.id = ?;
        """,
        (estimate_id,),
    ).fetchone()
    conn.close()

    context = {"estimate": estimate}
    status = 404 if estimate is None else 200
    return render(request, "estimates/estimate_detail.html", context, status=status)


def statistics(request):
    """Статистика смет по пользователям."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    stats = conn.execute(
        """
        SELECT
            u.name AS user_name,
            COUNT(e.id) AS estimates_count,
            ROUND(SUM(e.total), 2) AS total_spent,
            ROUND(AVG(e.total), 2) AS avg_cost
        FROM users u
        LEFT JOIN estimates e ON u.id = e.user_id
        GROUP BY u.id, u.name
        ORDER BY total_spent DESC;
        """
    ).fetchall()
    conn.close()

    context = {"stats": stats}
    return render(request, "estimates/statistics.html", context)
