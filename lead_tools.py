import sqlite3

DB_PATH = "mattress.db"

def save_lead(user_id, name, phone, contact_pref, model, size):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (user_id, name, phone, contact_pref, model, size)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, name, phone, contact_pref, model, size))

    conn.commit()
    conn.close()

    return "Lead saved successfully."


def list_leads():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, phone, contact_pref, model, size, timestamp
        FROM leads
        ORDER BY timestamp DESC
    """)

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No leads found."

    lines = []
    for r in rows:
        lines.append(
            f"#{r[0]} — {r[1]} ({r[2]}) wants {r[4]} {r[5]} via {r[3]} at {r[6]}"
        )

    return "\n".join(lines)
