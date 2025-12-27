# core/state.py
import sqlite3
import json
import uuid
from datetime import datetime

DB = "data/memory.db"

def _connect():
    return sqlite3.connect(DB)

def init_state_store():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS execution_state (
            execution_id TEXT PRIMARY KEY,
            status TEXT,
            reason TEXT,
            schema_snapshot TEXT,
            intent TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_state(schema_snapshot, intent, reason):
    execution_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO execution_state
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        execution_id,
        "BLOCKED",
        reason,
        json.dumps(schema_snapshot),
        json.dumps(intent),
        now,
        now
    ))
    conn.commit()
    conn.close()

    return execution_id

def load_state(execution_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT status, reason, schema_snapshot, intent
        FROM execution_state
        WHERE execution_id = ?
    """, (execution_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "status": row[0],
        "reason": row[1],
        "schema_snapshot": json.loads(row[2]),
        "intent": json.loads(row[3])
    }

def mark_resumed(execution_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        UPDATE execution_state
        SET status = ?, updated_at = ?
        WHERE execution_id = ?
    """, ("RESUMED", datetime.utcnow().isoformat(), execution_id))
    conn.commit()
    conn.close()
