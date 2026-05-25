import sqlite3

DB_PATH = "mattress.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # -----------------------------
    # Products table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            size TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # -----------------------------
    # Catalog table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            description TEXT,
            image_url TEXT
        )
    """)

    # -----------------------------
    # Leads table
    # -----------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            phone TEXT,
            contact_pref TEXT,
            model TEXT,
            size TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
