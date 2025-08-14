from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

# import os
from database import get_invoice_data
from pdf_styles import get_custom_styles, get_table_styles, LAYOUT


def generate_invoice_pdf(invoice_id, output_filename=None):
    """
    Generate a professional PDF invoice based on invoice ID.
    Implements FR3.1 (PDF Output), FR3.2 (Sender and Client Inclusion),
    FR4.3 (Item Listing), FR5.1 & FR5.2 (Totals), and FR6.4 (Footer Message)
    """

    # Get invoice data from database
    invoice_data, items = get_invoice_data(invoice_id)

    if not invoice_data:
        raise ValueError(f"Invoice with ID {invoice_id} not found")

    # Extract data from database result - updated structure includes paid field
    # Structure: (invoice_id, date_created, paid, sender_name, sender_address, sender_email, sender_phone,
    #            client_name, client_address, client_email, footer_message, sender_id, client_id, footer_message_id)
    (
        invoice_id,
        date_created,
        paid,
        sender_name,
        sender_address,
        sender_email,
        sender_phone,
        client_name,
        client_address,
        client_email,
        footer_message,
        sender_id,
        client_id,
        footer_message_id,
    ) = invoice_data

    # Set up output filename
    if not output_filename:
        output_filename = (
            f"invoice_{invoice_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

    # Create PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    story = []

    # Get styles
    styles = get_custom_styles()
    table_styles = get_table_styles()

    # Title
    story.append(Paragraph("INVOICE", styles["title"]))
    story.append(Spacer(1, LAYOUT["spacing"]["title_bottom"]))

    # Invoice info section
    invoice_info_data = [
        ["Invoice ID:", str(invoice_id)],
        [
            "Date:",
            (
                datetime.strptime(date_created, "%Y-%m-%d %H:%M:%S").strftime(
                    "%B %d, %Y"
                )
                if date_created
                else datetime.now().strftime("%B %d, %Y")
            ),
        ],
    ]

    invoice_info_table = Table(
        invoice_info_data, colWidths=LAYOUT["column_widths"]["invoice_info"]
    )
    invoice_info_table.setStyle(TableStyle(table_styles["invoice_info"]))

    story.append(invoice_info_table)
    story.append(Spacer(1, LAYOUT["spacing"]["section_bottom"]))

    # Sender and Client information side by side
    # FR3.2: Sender and Client Inclusion
    sender_address_formatted = (
        sender_address.replace("\n", "<br/>")
        if sender_address
        else "No address provided"
    )
    client_address_formatted = (
        client_address.replace("\n", "<br/>")
        if client_address
        else "No address provided"
    )

    sender_info = f"""<b>From:</b><br/>
    <b>{sender_name or "N/A"}</b><br/>
    {sender_address_formatted}<br/>
    {sender_email or ""}<br/>
    {sender_phone or ""}"""

    client_info = f"""<b>To:</b><br/>
    <b>{client_name or "N/A"}</b><br/>
    {client_address_formatted}<br/>
    {client_email or ""}"""

    contact_data = [
        [
            Paragraph(sender_info, styles["normal"]),
            Paragraph(client_info, styles["normal"]),
        ]
    ]

    contact_table = Table(
        contact_data, colWidths=LAYOUT["column_widths"]["contact_table"]
    )
    contact_table.setStyle(TableStyle(table_styles["contact_table"]))

    story.append(contact_table)
    story.append(Spacer(1, LAYOUT["spacing"]["section_bottom"]))

    # Items table
    # FR4.3: Item Listing on PDF
    story.append(Paragraph("Invoice Items", styles["header"]))
    story.append(Spacer(1, LAYOUT["spacing"]["items_header"]))

    # Table headers
    item_data = [["Description", "Quantity", "Unit Price", "Total"]]

    # Calculate totals as per FR5.1 and FR5.2
    subtotal = 0
    for item in items:
        item_name, amount, cost_per_unit = item
        line_total = amount * cost_per_unit
        subtotal += line_total

        item_data.append(
            [
                item_name,
                f"{amount:,.2f}",
                f"${cost_per_unit:,.2f}",
                f"${line_total:,.2f}",
            ]
        )

    # Add subtotal and grand total rows
    item_data.append(["", "", "Subtotal:", f"${subtotal:,.2f}"])
    item_data.append(["", "", "Grand Total:", f"${subtotal:,.2f}"])

    items_table = Table(item_data, colWidths=LAYOUT["column_widths"]["items_table"])
    items_table.setStyle(TableStyle(table_styles["items_table"]))

    story.append(items_table)
    story.append(Spacer(1, LAYOUT["spacing"]["footer_top"]))

    # Footer message
    # FR6.4: Footer Message Inclusion
    if footer_message:
        story.append(Paragraph("Notes:", styles["header"]))
        story.append(Spacer(1, LAYOUT["spacing"]["notes_spacing"]))
        story.append(Paragraph(footer_message, styles["normal"]))

    # Build PDF
    doc.build(story)

    return output_filename


def generate_sample_invoice_pdf():
    """Generate a sample invoice PDF for testing"""
    from database import init_db, create_sample_data

    # Initialize database and create sample data
    init_db()

    try:
        # Try to create sample data (will fail if already exists)
        invoice_id = create_sample_data()
        print(f"Created sample invoice with ID: {invoice_id}")
    except Exception as e:
        # If sample data already exists, use invoice ID 1
        invoice_id = 1
        print(f"Using existing invoice with ID: {invoice_id}")

    # Generate PDF
    try:
        output_file = generate_invoice_pdf(invoice_id)
        print(f"PDF generated successfully: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


if __name__ == "__main__":
    # Generate sample PDF when run directly
    generate_sample_invoice_pdf()
