import sqlite3

DB_PATH = "mattress.db"

def add_product(model, size, price):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO products (model, size, price) VALUES (?, ?, ?)",
        (model, size, price)
    )

    conn.commit()
    conn.close()
    return f"Added {model} {size} at ${price}."


def update_price(model, size, price):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "UPDATE products SET price = ? WHERE model = ? AND size = ?",
        (price, model, size)
    )

    conn.commit()
    conn.close()
    return f"Updated {model} {size} to ${price}."


def delete_product(model, size):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM products WHERE model = ? AND size = ?",
        (model, size)
    )

    conn.commit()
    conn.close()
    return f"Deleted {model} {size}."
