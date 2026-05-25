import sqlite3
import json

DB_PATH = "mattress.db"

def update_prices_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for model, sizes in data.items():
        for size, price in sizes.items():
            cur.execute(
                "UPDATE products SET price = ? WHERE model = ? AND size = ?",
                (price, model, size)
            )

    conn.commit()
    conn.close()
    print("Prices updated.")
