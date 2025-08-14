import pytest
import tempfile
import os
from unittest.mock import patch
from database import init_db


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_db_path = tmp_file.name
    
    # Patch the DB_FILE to use our temporary database
    with patch('database.DB_FILE', temp_db_path):
        init_db()
        yield temp_db_path
    
    # Clean up
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def sample_sender_data():
    """Sample sender data for testing"""
    return {
        "name": "Test Company Inc.",
        "address": "123 Business Street\nSuite 100\nBusiness City, ST 12345",
        "email": "contact@testcompany.com",
        "phone": "555-123-4567"
    }


@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return {
        "name": "Client Corporation",
        "address": "456 Client Avenue\nClient City, ST 67890",
        "email": "billing@clientcorp.com"
    }


@pytest.fixture
def sample_invoice_items():
    """Sample invoice items for testing"""
    return [
        {"description": "Web Development", "quantity": 40, "price": 75.00},
        {"description": "Consulting Services", "quantity": 10, "price": 100.00},
        {"description": "Design Work", "quantity": 5, "price": 50.00}
    ]


@pytest.fixture
def sample_footer_message():
    """Sample footer message for testing"""
    return "Thank you for your business! Payment is due within 30 days."


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for file outputs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_invoice_complete():
    """Complete mock invoice data with all related information"""
    return {
        "invoice_data": (
            1,  # invoice_id
            "2024-01-15 10:30:00",  # date_created
            False,  # paid
            "Test Company Inc.",  # sender_name
            "123 Business Street\nSuite 100\nBusiness City, ST 12345",  # sender_address
            "contact@testcompany.com",  # sender_email
            "555-123-4567",  # sender_phone
            "Client Corporation",  # client_name
            "456 Client Avenue\nClient City, ST 67890",  # client_address
            "billing@clientcorp.com",  # client_email
            "Thank you for your business!",  # footer_message
            "sender-uuid-123",  # sender_id
            "client-uuid-456",  # client_id
            1  # footer_message_id
        ),
        "items": [
            ("Web Development", 40, 75.00),
            ("Consulting Services", 10, 100.00),
            ("Design Work", 5, 50.00)
        ]
    }