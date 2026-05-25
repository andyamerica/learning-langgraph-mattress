import sqlite3

DB_PATH = "mattress.db"

def get_price(model: str, size: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT price FROM products WHERE model = ? AND size = ?",
        (model, size)
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


def get_catalog():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT model, description, image_url FROM catalog")
    rows = cur.fetchall()
    conn.close()

    return [
        {"model": r[0], "description": r[1], "image_url": r[2]}
        for r in rows
    ]


def get_lead_product_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT model, size, COUNT(*)
        FROM leads
        GROUP BY model, size
        ORDER BY COUNT(*) DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {"model": r[0], "size": r[1], "count": r[2]}
        for r in rows
    ]
