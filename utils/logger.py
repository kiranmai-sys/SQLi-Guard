import sqlite3
import os
from datetime import datetime

def ensure_tables(db_path):
    """Create security_events table if it doesn't exist."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip TEXT,
            username TEXT,
            reason TEXT,
            pattern TEXT,
            snippet TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(db_path, ip, username, reason, pattern, snippet, user_agent):
    """Log a security event to the database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO security_events (ip, username, reason, pattern, snippet, user_agent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (ip, username, reason, pattern, snippet, user_agent))
    conn.commit()
    conn.close()