import sqlite3
DB_NAME = "commissions.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

# initialize_database function creates the database that will store all commissions 
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

# add_commission function takes in the commission info and adds a commission to the database 
def add_commission(client, title, type_, price, deadline, status, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO commissions (client, title, type, price, deadline, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client, title, type_, price, deadline, status, notes))
    conn.commit()
    conn.close()

# get_commission returns one commission by its unique ID
def get_commission_by_id(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commissions WHERE id = ?", (comm_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# update_commission updates/overwrites the information for a specific commission
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

# delete_commission gets a commission according to its ID and deletes it from the database
def delete_commission(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM commissions WHERE id = ?", (comm_id,))
    conn.commit()
    conn.close()

# mark_complete takes a commission according to its ID and updates its status column in the database
def mark_complete(comm_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE commissions SET status = 'Completed' WHERE id = ?", (comm_id,))
    conn.commit()
    conn.close()

# get_commissions_by_status grabs commissions that matches a certain status
def get_commissions_by_status(status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commissions WHERE status = ?", (status,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_commissions(status=None, sort_by="deadline"):
    """
    status: None or "All" or one of STATUS_OPTIONS
    sort_by: one of: id, client, title, type, price, deadline, status
    """
    allowed = {
        "id": "id",
        "client": "client COLLATE NOCASE",
        "title": "title COLLATE NOCASE",
        "type": "type COLLATE NOCASE",
        "price": "price",
        "deadline": "deadline",
        "status": "status COLLATE NOCASE",
    }

    order_clause = allowed.get(sort_by, "deadline")

    conn = get_connection()
    cursor = conn.cursor()

    if status is None or status == "All":
        cursor.execute(f"SELECT * FROM commissions ORDER BY {order_clause} ASC")
    else:
        cursor.execute(f"SELECT * FROM commissions WHERE status = ? ORDER BY {order_clause} ASC", (status,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# get_summary calculates total comissions, completed comissions, and total income
def get_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM commissions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM commissions WHERE status='Completed'")
    completed = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM commissions WHERE status='In Progress'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM commissions WHERE status='Not Started'")
    not_started = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(price) FROM commissions WHERE status='Completed'")
    income = cursor.fetchone()[0] or 0

    conn.close()
    return total, completed, in_progress, not_started, income

# get_income_by_type 
def get_income_by_type():
    """
    Returns [(type, total_income), ...] for Completed commissions only
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(type, 'Other') as type, SUM(price)
        FROM commissions
        WHERE status='Completed'
        GROUP BY COALESCE(type, 'Other')
        HAVING SUM(price) > 0
        ORDER BY SUM(price) DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows



# Initialize
initialize_database()