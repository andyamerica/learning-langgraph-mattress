import sqlite3
#from mattress_master_data import PRICES, CATALOG

DB_PATH = "mattress.db"

def load_master_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -----------------------------
    # Load product prices
    # -----------------------------
    for model, sizes in PRICES.items():
        for size, price in sizes.items():
            cur.execute("""
                INSERT INTO products (model, size, price)
                VALUES (?, ?, ?)
            """, (model, size, price))

    # -----------------------------
    # Load catalog info
    # -----------------------------
    for model, info in CATALOG.items():
        cur.execute("""
            INSERT INTO catalog (model, description, image_url)
            VALUES (?, ?, ?)
        """, (
            model,
            info.get("description"),
            info.get("image_url")
        ))

    conn.commit()
    conn.close()
    print("Master data loaded into SQLite.")

if __name__ == "__main__":
    load_master_data()
