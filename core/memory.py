import sqlite3
from datetime import datetime

DB = "data/memory.db"

def record_event(status, message):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            time TEXT,
            status TEXT,
            message TEXT
        )
    """)
    cur.execute(
        "INSERT INTO events VALUES (?,?,?)",
        (datetime.now().isoformat(), status, message)
    )
    conn.commit()
    conn.close()
