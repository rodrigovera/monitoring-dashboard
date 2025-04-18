# database.py
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("monitoring.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_clients_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

