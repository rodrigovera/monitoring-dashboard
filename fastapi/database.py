# database.py

import sqlite3

DB_NAME = "monitoring.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_clients_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            api_url TEXT NOT NULL,
            token TEXT,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_client(nombre, email, api_url, token=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clients (nombre, email, api_url, token)
        VALUES (?, ?, ?, ?)
    ''', (nombre, email, api_url, token))
    conn.commit()
    conn.close()
