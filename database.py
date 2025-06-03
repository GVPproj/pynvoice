import sqlite3
import os

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
    conn.commit()
    conn.close()


def list_senders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, address, email, phone FROM sender")
    senders = c.fetchall()
    conn.close()
    return senders
