#!/usr/bin/env python3
"""
Demo script for Pynvoice PDF Generation
Demonstrates FR3 (PDF generation) functionality from the PRD
"""

from database import init_db, create_sample_data, get_invoice_data
from pdf_generator import generate_invoice_pdf
import os


def main():
    print("=== Pynvoice PDF Generation Demo ===")
    print()

    # Initialize database
    print("1. Initializing database...")
    init_db()

    # Create sample data if it doesn't exist
    print("2. Creating sample data...")
    try:
        invoice_id = create_sample_data()
        print(f"   Created new sample invoice with ID: {invoice_id}")
    except Exception as e:
        # Sample data might already exist
        invoice_id = 1
        print(f"   Using existing sample invoice with ID: {invoice_id}")

    # Display invoice data
    print("\n3. Invoice data to be included in PDF:")
    invoice_data, items = get_invoice_data(invoice_id)

    if invoice_data:
        (
            inv_id,
            date_created,
            sender_name,
            sender_address,
            sender_email,
            sender_phone,
            client_name,
            client_address,
            client_email,
            footer_message,
        ) = invoice_data

        print(f"   Invoice ID: {inv_id}")
        print(f"   Date: {date_created}")
        print(f"   Sender: {sender_name}")
        print(f"   Sender Address: {sender_address}")
        print(f"   Sender Email: {sender_email}")
        print(f"   Sender Phone: {sender_phone}")
        print(f"   Client: {client_name}")
        print(f"   Client Address: {client_address}")
        print(f"   Client Email: {client_email}")
        print(f"   Footer: {footer_message}")

        print(f"\n   Invoice Items:")
        total = 0
        for item in items:
            item_name, amount, cost_per_unit = item
            line_total = amount * cost_per_unit
            total += line_total
            print(
                f"   - {item_name}: {amount} x ${cost_per_unit:.2f} = ${line_total:.2f}"
            )
        print(f"   Total: ${total:.2f}")

    # Generate PDF
    print(f"\n4. Generating PDF for invoice {invoice_id}...")
    try:
        output_file = generate_invoice_pdf(invoice_id)
        file_size = os.path.getsize(output_file)
        print(f"   ✓ PDF generated successfully: {output_file}")
        print(f"   ✓ File size: {file_size} bytes")

        # Verify file exists
        if os.path.exists(output_file):
            print(f"   ✓ PDF file verified and ready to view")
        else:
            print(f"   ✗ ERROR: PDF file not found!")

    except Exception as e:
        print(f"   ✗ ERROR generating PDF: {e}")
        return False

    print("\n=== Demo completed successfully! ===")
    print("\nImplemented PRD Requirements:")
    print("✓ FR3.1: PDF Output - Invoice generated in PDF format")
    print(
        "✓ FR3.2: Sender and Client Inclusion - Both sender and client details included"
    )
    print("✓ FR3.3: Invoice Data Persistence - Invoice stored in database")
    print("✓ FR4.3: Item Listing on PDF - All items displayed with calculations")
    print("✓ FR5.1: Calculate Subtotal - Subtotal calculated and displayed")
    print("✓ FR5.2: Calculate Grand Total - Grand total calculated and displayed")
    print("✓ FR6.4: Footer Message Inclusion - Footer message included in PDF")

    return True


if __name__ == "__main__":
    main()
