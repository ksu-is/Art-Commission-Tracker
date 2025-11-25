import sqlite3
DB_NAME = "commissions.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

#initialize_database function creates the database that will store all commissions 
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

#add_commission function takes in the commission info and adds a commission to the database 
def add_commission(client, title, type_, price, deadline, status, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO commissions (client, title, type, price, deadline, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client, title, type_, price, deadline, status, notes))
    conn.commit()
    conn.close()

#get_commission returns one commission by its unique ID
def get_commission(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commissions WHERE id = ?", (comm_id,))
    row = cursor.fetchone()
    conn.close()
    return row

#update_commission updates/overwrites the information for a specific commission
def update_commission(comm_id, client, title, type_, price, deadline, status, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE commissions
        SET client=?, title=?, type=?, price=?, deadline=?, status=?, notes=?
        WHERE id=?
    """, (client, title, type_, price, deadline, status, notes, comm_id))
    conn.commit()
    conn.close()

#delete_commission gets a commission according to its ID and deletes it from the database
def delete_commission(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM commissions WHERE id = ?", (comm_id,))
    conn.commit()
    conn.close()

#mark_complete takes a commission according to its ID and updates its status  column in the database
def mark_complete(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE commissions SET status = 'Completed' WHERE id = ?", (comm_id,))
    conn.commit()
    conn.close()