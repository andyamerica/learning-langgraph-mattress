import sqlite3

conn = sqlite3.connect("mattress.db")
cur = conn.cursor()
cur.execute("SELECT model, size, price FROM products")
print(cur.fetchall())
conn.close()
