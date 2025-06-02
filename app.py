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


def create_sender():
    print("--- Create New Sender ---")
    name = input("Name: ").strip()
    address = input("Address: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sender (name, address, email, phone) VALUES (?, ?, ?, ?)",
        (name, address, email, phone),
    )
    conn.commit()
    conn.close()
    print("Sender created successfully.")


def list_senders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, address, email, phone FROM sender")
    senders = c.fetchall()
    conn.close()
    return senders


def choose_sender():
    senders = list_senders()
    if not senders:
        print("No senders found. Please create a sender first.")
        return None
    print("--- Existing Senders ---")
    for idx, sender in enumerate(senders, 1):
        print(f"{idx}. {sender[1]} | {sender[2]} | {sender[3]} | {sender[4]}")
    choice = input("Select sender by number: ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(senders):
            return senders[idx]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input.")
        return None


def main():
    init_db()
    while True:
        print("\n--- Sender Management ---")
        print("1. Create New Sender")
        print("2. Choose Existing Sender")
        print("3. Exit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            create_sender()
        elif choice == "2":
            sender = choose_sender()
            if sender:
                print(f"Selected sender: {sender[1]}")
        elif choice == "3":
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
