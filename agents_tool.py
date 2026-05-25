import sqlite3
from datetime import datetime

DB_PATH = "mattress_agent_state.db"

# -----------------------------
# Helper: DB connection
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)


# -----------------------------
# Save a customer lead
# -----------------------------
def save_lead(name, phone, contact_pref, model, size):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (name, phone, contact_pref, model, size)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, contact_pref, model, size))

    conn.commit()
    conn.close()

    return f"Lead saved for {name} ({model} - {size})."


# -----------------------------
# List all leads
# -----------------------------
def list_leads():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name, phone, contact_pref, model, size, created_at FROM leads ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No leads found."

    formatted = []
    for r in rows:
        formatted.append(
            f"#{r[0]} — {r[1]} | {r[2]} | {r[3]} | {r[4]} {r[5]} | {r[6]}"
        )

    return "\n".join(formatted)


# -----------------------------
# Log user interaction
# -----------------------------
def log_interaction(user_id, message, intent):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO interactions (user_id, message, intent)
        VALUES (?, ?, ?)
    """, (user_id, message, intent))

    conn.commit()
    conn.close()

    return "Interaction logged."


# -----------------------------
# Admin: Status
# -----------------------------
def admin_status():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM leads")
    lead_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM interactions")
    interaction_count = cur.fetchone()[0]

    conn.close()

    return (
        f"Agent Status:\n"
        f"- Leads stored: {lead_count}\n"
        f"- Interactions logged: {interaction_count}\n"
        f"- DB: mattress_agent_state.db\n"
        f"- Last check: {datetime.now()}"
    )


# -----------------------------
# Admin: Restart (simulated)
# -----------------------------
def admin_restart():
    return "Agent restart simulated. (In real deployment, this would restart the service.)"
