import sqlite3

DB_FILE = "pynvoice.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sender (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def list_senders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, address, email, phone FROM sender")
    senders = c.fetchall()
    conn.close()
    return senders


def list_clients():
    """List all clients from the database as per FR2.2"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, address, email FROM client")
    clients = c.fetchall()
    conn.close()
    return clients


def create_client(name, address=None, email=None):
    """Create a new client as per FR2.1 - name is mandatory, address and email are optional"""
    if not name or not name.strip():
        raise ValueError("Client name is required")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO client (name, address, email) VALUES (?, ?, ?)",
            (
                name.strip(),
                address.strip() if address else None,
                email.strip() if email else None,
            ),
        )
        conn.commit()
        client_id = c.lastrowid
        return client_id
    finally:
        conn.close()
