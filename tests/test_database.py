import pytest
import sqlite3
import tempfile
import os
from unittest.mock import patch

from database import (
    init_db,
    create_sender,
    list_senders,
    update_sender,
    create_client,
    list_clients,
    update_client,
    create_footer_message,
    list_footer_messages,
    update_footer_message,
    create_invoice,
    list_invoices,
    # update_invoice,
    add_invoice_item,
    get_invoice_data,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        temp_db_path = tmp_file.name

    # Patch the DB_FILE to use our temporary database
    with patch("database.DB_FILE", temp_db_path):
        init_db()
        yield temp_db_path

    # Clean up
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


class TestDatabaseInit:
    def test_init_db_creates_tables(self, temp_db):
        """Test that init_db creates all required tables"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            "sender",
            "client",
            "footer_message",
            "invoice",
            "invoice_item",
        }
        assert expected_tables.issubset(tables)

        conn.close()


class TestSenderOperations:
    def test_create_and_list_sender(self, temp_db):
        """Test creating and retrieving a sender"""
        with patch("database.DB_FILE", temp_db):
            # Create a sender
            sender_id = create_sender(
                "Test Company", "123 Main St", "test@example.com", "555-1234"
            )
            assert sender_id is not None

            # Retrieve senders
            senders = list_senders()
            assert len(senders) == 1
            assert senders[0][1] == "Test Company"  # name field
            assert senders[0][2] == "123 Main St"  # address field

    def test_update_sender(self, temp_db):
        """Test updating a sender"""
        with patch("database.DB_FILE", temp_db):
            # Create and update a sender
            sender_id = create_sender(
                "Original Name", "Original Address", "old@example.com", "555-0000"
            )
            update_sender(
                sender_id,
                "Updated Name",
                "Updated Address",
                "new@example.com",
                "555-9999",
            )

            # Verify update
            senders = list_senders()
            sender = next(s for s in senders if s[0] == sender_id)
            assert sender[1] == "Updated Name"
            assert sender[3] == "new@example.com"

    def test_create_sender_validation(self, temp_db):
        """Test sender creation validation"""
        with patch("database.DB_FILE", temp_db):
            # Test empty name validation
            with pytest.raises(ValueError, match="Sender name is required"):
                create_sender("", "Address", "email@example.com", "555-1111")


class TestClientOperations:
    def test_create_and_list_client(self, temp_db):
        """Test creating and retrieving a client"""
        with patch("database.DB_FILE", temp_db):
            client_id = create_client("Test Client", "456 Oak St", "client@example.com")
            assert client_id is not None

            clients = list_clients()
            assert len(clients) == 1
            assert clients[0][1] == "Test Client"

    def test_update_client(self, temp_db):
        """Test updating a client"""
        with patch("database.DB_FILE", temp_db):
            client_id = create_client(
                "Original Client", "Original Address", "old@client.com"
            )
            update_client(
                client_id, "Updated Client", "Updated Address", "new@client.com"
            )

            clients = list_clients()
            client = next(c for c in clients if c[0] == client_id)
            assert client[1] == "Updated Client"

    def test_create_client_validation(self, temp_db):
        """Test client creation validation"""
        with patch("database.DB_FILE", temp_db):
            # Test empty name validation
            with pytest.raises(ValueError, match="Client name is required"):
                create_client("", "Address", "email@client.com")


class TestFooterMessageOperations:
    def test_create_and_list_footer_message(self, temp_db):
        """Test creating and retrieving footer messages"""
        with patch("database.DB_FILE", temp_db):
            message_id = create_footer_message("Thank you for your business!")
            assert message_id is not None

            messages = list_footer_messages()
            assert len(messages) == 1
            assert messages[0][1] == "Thank you for your business!"

    def test_update_footer_message(self, temp_db):
        """Test updating a footer message"""
        with patch("database.DB_FILE", temp_db):
            message_id = create_footer_message("Original message")
            update_footer_message(message_id, "Updated message")

            messages = list_footer_messages()
            message = next(m for m in messages if m[0] == message_id)
            assert message[1] == "Updated message"

    def test_create_footer_message_validation(self, temp_db):
        """Test footer message creation validation"""
        with patch("database.DB_FILE", temp_db):
            # Test empty message validation
            with pytest.raises(ValueError, match="Footer message is required"):
                create_footer_message("")


class TestInvoiceOperations:
    def test_create_invoice_with_dependencies(self, temp_db):
        """Test creating an invoice with required dependencies"""
        with patch("database.DB_FILE", temp_db):
            # Create dependencies
            sender_id = create_sender(
                "Test Sender", "Address", "sender@test.com", "555-0001"
            )
            client_id = create_client("Test Client", "Address", "client@test.com")
            message_id = create_footer_message("Thank you!")

            # Create invoice
            invoice_id = create_invoice(sender_id, client_id, message_id)
            assert invoice_id is not None

            # Verify invoice exists
            invoices = list_invoices()
            assert len(invoices) == 1
            assert invoices[0][1] == "Test Sender"  # sender_name field
            assert invoices[0][2] == "Test Client"  # client_name field


class TestInvoiceItemOperations:
    def test_add_invoice_item(self, temp_db):
        """Test adding invoice items"""
        with patch("database.DB_FILE", temp_db):
            # Create dependencies
            sender_id = create_sender(
                "Test Sender", "Address", "sender@test.com", "555-0001"
            )
            client_id = create_client("Test Client", "Address", "client@test.com")
            invoice_id = create_invoice(sender_id, client_id, None)

            # Add invoice item
            item_id = add_invoice_item(invoice_id, "Test Service", 2, 100.00)
            assert item_id is not None

            # Verify item exists using get_invoice_data
            invoice_data, items = get_invoice_data(invoice_id)
            assert len(items) == 1
            assert items[0][0] == "Test Service"  # item_name field
            assert items[0][1] == 2  # amount field
            assert items[0][2] == 100.00  # cost_per_unit field

    def test_add_invoice_item_validation(self, temp_db):
        """Test invoice item creation validation"""
        with patch("database.DB_FILE", temp_db):
            # Create dependencies
            sender_id = create_sender(
                "Test Sender", "Address", "sender@test.com", "555-0001"
            )
            client_id = create_client("Test Client", "Address", "client@test.com")
            invoice_id = create_invoice(sender_id, client_id, None)

            # Test validation
            with pytest.raises(ValueError, match="Item name is required"):
                add_invoice_item(invoice_id, "", 2, 100.00)

            with pytest.raises(ValueError, match="Amount must be positive"):
                add_invoice_item(invoice_id, "Service", -1, 100.00)

            with pytest.raises(ValueError, match="Cost per unit must be positive"):
                add_invoice_item(invoice_id, "Service", 2, -100.00)

