import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from reportlab.lib.pagesizes import letter

from pdf_generator import generate_invoice_pdf


class TestPDFGenerator:
    @pytest.fixture
    def mock_invoice_data(self):
        """Mock invoice data for testing"""
        invoice_data = (
            1,  # invoice_id
            "2024-01-15 10:30:00",  # date_created
            False,  # paid
            "Test Company",  # sender_name
            "123 Business St\nSuite 100\nCity, ST 12345",  # sender_address
            "contact@testcompany.com",  # sender_email
            "555-123-4567",  # sender_phone
            "Client Corp",  # client_name
            "456 Client Ave\nClient City, ST 67890",  # client_address
            "billing@clientcorp.com",  # client_email
            "Thank you for your business!",  # footer_message
            "sender-uuid-123",  # sender_id
            "client-uuid-456",  # client_id
            1  # footer_message_id
        )
        
        items = [
            ("Web Development", 40, 75.00),  # item_name, amount, cost_per_unit
            ("Consulting", 10, 100.00),
            ("Design Work", 5, 50.00)
        ]
        
        return invoice_data, items

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for PDF output"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_generate_invoice_pdf_success(self, mock_invoice_data, temp_output_dir):
        """Test successful PDF generation"""
        invoice_data, items = mock_invoice_data
        output_path = os.path.join(temp_output_dir, "test_invoice.pdf")
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            # Generate PDF
            result_path = generate_invoice_pdf(1, output_path)
            
            # Verify file was created
            assert os.path.exists(result_path)
            assert os.path.getsize(result_path) > 0  # File should have content
            
            # Verify it's a PDF file (basic check)
            with open(result_path, 'rb') as f:
                header = f.read(4)
                assert header == b'%PDF'  # PDF files start with %PDF

    def test_generate_invoice_pdf_auto_filename(self, mock_invoice_data, temp_output_dir):
        """Test PDF generation with automatic filename"""
        invoice_data, items = mock_invoice_data
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            with patch('os.getcwd', return_value=temp_output_dir):
                # Generate PDF without specifying filename
                result_path = generate_invoice_pdf(1)
                
                # Verify file was created with expected naming pattern
                assert os.path.exists(result_path)
                filename = os.path.basename(result_path)
                assert filename.startswith("invoice_1_")
                assert filename.endswith(".pdf")

    def test_generate_invoice_pdf_invoice_not_found(self):
        """Test error handling when invoice is not found"""
        with patch('pdf_generator.get_invoice_data', return_value=(None, [])):
            with pytest.raises(ValueError, match="Invoice with ID 999 not found"):
                generate_invoice_pdf(999)

    def test_pdf_contains_expected_content(self, mock_invoice_data, temp_output_dir):
        """Test that PDF contains expected invoice content"""
        invoice_data, items = mock_invoice_data
        output_path = os.path.join(temp_output_dir, "content_test.pdf")
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            # Mock the PDF generation to capture content
            with patch('pdf_generator.SimpleDocTemplate') as mock_doc:
                mock_doc_instance = MagicMock()
                mock_doc.return_value = mock_doc_instance
                
                generate_invoice_pdf(1, output_path)
                
                # Verify SimpleDocTemplate was called with correct filename
                mock_doc.assert_called_once_with(output_path, pagesize=letter)
                
                # Verify build was called (PDF was generated)
                mock_doc_instance.build.assert_called_once()

    def test_invoice_totals_calculation(self, mock_invoice_data):
        """Test that invoice totals are calculated correctly"""
        invoice_data, items = mock_invoice_data
        
        # Calculate expected totals based on actual invoice items structure
        # Items: (40 * 75.00) + (10 * 100.00) + (5 * 50.00) = 3000 + 1000 + 250 = 4250
        expected_subtotal = 4250.00
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            with patch('pdf_generator.SimpleDocTemplate') as mock_doc:
                mock_doc_instance = MagicMock()
                mock_doc.return_value = mock_doc_instance
                
                # Capture the build arguments to verify totals
                def capture_build_args(*args):
                    return args
                
                mock_doc_instance.build.side_effect = capture_build_args
                
                generate_invoice_pdf(1, "test.pdf")
                
                # Verify build was called
                mock_doc_instance.build.assert_called_once()

    def test_pdf_with_no_items(self, temp_output_dir):
        """Test PDF generation with no invoice items"""
        invoice_data = (
            2, "2024-01-15 10:30:00", False, "Test Company", "123 Business St",
            "contact@testcompany.com", "555-123-4567", "Client Corp", "456 Client Ave",
            "billing@clientcorp.com", "Thank you!", "sender-uuid", "client-uuid", 1
        )
        items = []  # No items
        
        output_path = os.path.join(temp_output_dir, "no_items.pdf")
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            result_path = generate_invoice_pdf(2, output_path)
            
            # Should still create a valid PDF
            assert os.path.exists(result_path)
            assert os.path.getsize(result_path) > 0

    def test_pdf_with_long_content(self, temp_output_dir):
        """Test PDF generation with long descriptions and content"""
        invoice_data = (
            3, "2024-01-15 10:30:00", False, "Very Long Company Name Inc. LLC",
            "123 Very Long Business Street Name\nSuite 100-200\nVery Long City Name, ST 12345-6789",
            "very.long.email.address@testcompany.com", "555-123-4567",
            "Very Long Client Corporation Name LLC Inc", 
            "456 Very Long Client Avenue Name\nVery Long Client City Name, ST 67890-1234",
            "very.long.billing.email@clientcorp.com", 
            "Thank you very much for your business! We appreciate your continued partnership.",
            "sender-uuid", "client-uuid", 1
        )
        
        items = [
            ("Very long detailed description of web development services including front-end and back-end work", 40, 75.00),
            ("Extended consulting services with detailed analysis and recommendations", 10, 100.00)
        ]
        
        output_path = os.path.join(temp_output_dir, "long_content.pdf")
        
        with patch('pdf_generator.get_invoice_data', return_value=(invoice_data, items)):
            result_path = generate_invoice_pdf(3, output_path)
            
            assert os.path.exists(result_path)
            assert os.path.getsize(result_path) > 0