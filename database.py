import sqlite3
import uuid

DB_FILE = "pynvoice.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sender (
            id TEXT PRIMARY KEY,
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
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS footer_message (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS invoice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id TEXT NOT NULL,
            client_id TEXT NOT NULL,
            footer_message_id INTEGER,
            paid BOOLEAN DEFAULT FALSE,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES sender (id),
            FOREIGN KEY (client_id) REFERENCES client (id),
            FOREIGN KEY (footer_message_id) REFERENCES footer_message (id)
        )
    """
    )

    # Add paid column to existing tables if it doesn't exist
    try:
        c.execute("ALTER TABLE invoice ADD COLUMN paid BOOLEAN DEFAULT FALSE")
    except sqlite3.OperationalError:
        # Column already exists
        pass

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS invoice_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL NOT NULL,
            cost_per_unit REAL NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES invoice (id)
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


def list_footer_messages():
    """List all footer messages from the database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, message FROM footer_message")
    messages = c.fetchall()
    conn.close()
    return messages


def list_invoices():
    """List all invoices with their basic information including paid status"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        SELECT 
            i.id,
            s.name as sender_name,
            c.name as client_name,
            i.date_created,
            i.paid
        FROM invoice i
        LEFT JOIN sender s ON i.sender_id = s.id
        LEFT JOIN client c ON i.client_id = c.id
        ORDER BY i.date_created DESC
    """
    )
    invoices = c.fetchall()
    conn.close()
    return invoices


def create_client(name, address=None, email=None):
    """Create a new client as per FR2.1 - name is mandatory, address and email are optional"""
    if not name or not name.strip():
        raise ValueError("Client name is required")

    client_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO client (id, name, address, email) VALUES (?, ?, ?, ?)",
            (
                client_id,
                name.strip(),
                address.strip() if address else None,
                email.strip() if email else None,
            ),
        )
        conn.commit()
        return client_id
    finally:
        conn.close()


def create_sender(name, address=None, email=None, phone=None):
    """Create a new sender"""
    if not name or not name.strip():
        raise ValueError("Sender name is required")

    sender_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO sender (id, name, address, email, phone) VALUES (?, ?, ?, ?, ?)",
            (
                sender_id,
                name.strip(),
                address.strip() if address else None,
                email.strip() if email else None,
                phone.strip() if phone else None,
            ),
        )
        conn.commit()
        return sender_id
    finally:
        conn.close()


def create_footer_message(message):
    """Create a new footer message"""
    if not message or not message.strip():
        raise ValueError("Footer message is required")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO footer_message (message) VALUES (?)",
            (message.strip(),),
        )
        conn.commit()
        footer_id = c.lastrowid
        return footer_id
    finally:
        conn.close()


def update_client(client_id, name, address=None, email=None):
    """Update an existing client"""
    if not name or not name.strip():
        raise ValueError("Client name is required")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE client SET name = ?, address = ?, email = ? WHERE id = ?",
            (
                name.strip(),
                address.strip() if address else None,
                email.strip() if email else None,
                client_id,
            ),
        )
        conn.commit()
        if c.rowcount == 0:
            raise ValueError(f"Client with ID {client_id} not found")
        return client_id
    finally:
        conn.close()


def update_sender(sender_id, name, address=None, email=None, phone=None):
    """Update an existing sender"""
    if not name or not name.strip():
        raise ValueError("Sender name is required")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE sender SET name = ?, address = ?, email = ?, phone = ? WHERE id = ?",
            (
                name.strip(),
                address.strip() if address else None,
                email.strip() if email else None,
                phone.strip() if phone else None,
                sender_id,
            ),
        )
        conn.commit()
        if c.rowcount == 0:
            raise ValueError(f"Sender with ID {sender_id} not found")
        return sender_id
    finally:
        conn.close()


def update_footer_message(footer_id, message):
    """Update an existing footer message"""
    if not message or not message.strip():
        raise ValueError("Footer message is required")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE footer_message SET message = ? WHERE id = ?",
            (message.strip(), footer_id),
        )
        conn.commit()
        if c.rowcount == 0:
            raise ValueError(f"Footer message with ID {footer_id} not found")
        return footer_id
    finally:
        conn.close()


def create_invoice(sender_id, client_id, footer_message_id=None, paid=False):
    """Create a new invoice"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO invoice (sender_id, client_id, footer_message_id, paid) VALUES (?, ?, ?, ?)",
            (sender_id, client_id, footer_message_id, paid),
        )
        conn.commit()
        invoice_id = c.lastrowid
        return invoice_id
    finally:
        conn.close()


def update_invoice(
    invoice_id, sender_id, client_id, footer_message_id=None, paid=False
):
    """Update an existing invoice"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE invoice SET sender_id = ?, client_id = ?, footer_message_id = ?, paid = ? WHERE id = ?",
            (sender_id, client_id, footer_message_id, paid, invoice_id),
        )
        conn.commit()
        if c.rowcount == 0:
            raise ValueError(f"Invoice with ID {invoice_id} not found")
        return invoice_id
    finally:
        conn.close()


def add_invoice_item(invoice_id, item_name, amount, cost_per_unit):
    """Add an item to an invoice"""
    if not item_name or not item_name.strip():
        raise ValueError("Item name is required")
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if cost_per_unit <= 0:
        raise ValueError("Cost per unit must be positive")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO invoice_item (invoice_id, item_name, amount, cost_per_unit) VALUES (?, ?, ?, ?)",
            (invoice_id, item_name.strip(), amount, cost_per_unit),
        )
        conn.commit()
        item_id = c.lastrowid
        return item_id
    finally:
        conn.close()


def get_invoice_data(invoice_id):
    """Get complete invoice data including sender, client, items, and footer message"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Get invoice with sender and client details
    c.execute(
        """
        SELECT 
            i.id as invoice_id,
            i.date_created,
            i.paid,
            s.name as sender_name, s.address as sender_address, s.email as sender_email, s.phone as sender_phone,
            c.name as client_name, c.address as client_address, c.email as client_email,
            f.message as footer_message,
            i.sender_id,
            i.client_id,
            i.footer_message_id
        FROM invoice i
        LEFT JOIN sender s ON i.sender_id = s.id
        LEFT JOIN client c ON i.client_id = c.id
        LEFT JOIN footer_message f ON i.footer_message_id = f.id
        WHERE i.id = ?
    """,
        (invoice_id,),
    )

    invoice_data = c.fetchone()

    # Get invoice items
    c.execute(
        """
        SELECT item_name, amount, cost_per_unit
        FROM invoice_item
        WHERE invoice_id = ?
    """,
        (invoice_id,),
    )

    items = c.fetchall()
    conn.close()

    return invoice_data, items


def create_sample_data():
    """Create sample data for testing PDF generation"""
    # Create sample sender
    sender_id = create_sender(
        name="John Doe Consulting",
        address="123 Business St, Suite 100\nNew York, NY 10001",
        email="john@doeconsulting.com",
        phone="(555) 123-4567",
    )

    # Create sample client
    client_id = create_client(
        name="Acme Corporation",
        address="456 Client Ave\nLos Angeles, CA 90210",
        email="billing@acmecorp.com",
    )

    # Create sample footer message
    footer_id = create_footer_message(
        "Payment due within 30 days. Thank you for your business!"
    )

    # Create sample invoice
    invoice_id = create_invoice(sender_id, client_id, footer_id)

    # Add sample items
    add_invoice_item(invoice_id, "Consulting Hours", 40, 125.00)
    add_invoice_item(invoice_id, "Project Analysis", 1, 500.00)
    add_invoice_item(invoice_id, "Documentation", 8, 75.00)

    return invoice_id
