import sqlite3
DB_NAME = "commissions.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT,
            price REAL,
            deadline TEXT,
            status TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_commission(client, title, type_, price, deadline, status, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO commissions (client, title, type, price, deadline, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client, title, type_, price, deadline, status, notes))
    conn.commit()
    conn.close()

