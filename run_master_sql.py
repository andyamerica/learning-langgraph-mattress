import sqlite3
import os

DB_PATH = "mattress.db"
SQL_PATH = "master_data.sql"

print("=== Debug Start ===")

print("Current working directory:", os.getcwd())
print("DB exists:", os.path.exists(DB_PATH))
print("SQL exists:", os.path.exists(SQL_PATH))

try:
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()
    print("SQL file loaded successfully.")
except Exception as e:
    print("Error reading SQL file:", e)

try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("Connected to DB.")
except Exception as e:
    print("Error connecting to DB:", e)

try:
    cur.executescript(sql_script)
    conn.commit()
    conn.close()
    print("SQL executed successfully.")
except Exception as e:
    print("Error executing SQL:", e)

print("=== Debug End ===")
