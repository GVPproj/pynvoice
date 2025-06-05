from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from datetime import datetime
import os
from database import get_invoice_data


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

    # Extract data from database result
    (
        invoice_id,
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

    # Set up output filename
    if not output_filename:
        output_filename = (
            f"invoice_{invoice_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

    # Create PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2E4057"),
        alignment=TA_CENTER,
        spaceAfter=30,
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#2E4057"),
        fontName="Helvetica-Bold",
    )

    normal_style = ParagraphStyle(
        "NormalStyle", parent=styles["Normal"], fontSize=10, textColor=colors.black
    )

    # Title
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 20))

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

    invoice_info_table = Table(invoice_info_data, colWidths=[1.5 * inch, 2 * inch])
    invoice_info_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(invoice_info_table)
    story.append(Spacer(1, 30))

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
    <b>{sender_name or 'N/A'}</b><br/>
    {sender_address_formatted}<br/>
    {sender_email or ''}<br/>
    {sender_phone or ''}"""

    client_info = f"""<b>To:</b><br/>
    <b>{client_name or 'N/A'}</b><br/>
    {client_address_formatted}<br/>
    {client_email or ''}"""

    contact_data = [
        [Paragraph(sender_info, normal_style), Paragraph(client_info, normal_style)]
    ]

    contact_table = Table(contact_data, colWidths=[3.5 * inch, 3.5 * inch])
    contact_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    story.append(contact_table)
    story.append(Spacer(1, 40))

    # Items table
    # FR4.3: Item Listing on PDF
    story.append(Paragraph("Invoice Items", header_style))
    story.append(Spacer(1, 10))

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

    items_table = Table(
        item_data, colWidths=[3 * inch, 1 * inch, 1.25 * inch, 1.25 * inch]
    )
    items_table.setStyle(
        TableStyle(
            [
                # Header row styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E4057")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                # Data rows styling
                ("FONTNAME", (0, 1), (-1, -3), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -3), 10),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -3),
                    [colors.white, colors.HexColor("#F8F9FA")],
                ),
                # Subtotal and total rows styling
                ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -2), (-1, -1), 11),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E9ECEF")),
                # Alignment
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                # Borders
                ("GRID", (0, 0), (-1, -3), 1, colors.HexColor("#DEE2E6")),
                ("LINEBELOW", (0, -2), (-1, -2), 1, colors.HexColor("#6C757D")),
                ("LINEBELOW", (0, -1), (-1, -1), 2, colors.HexColor("#2E4057")),
                # Padding
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )

    story.append(items_table)
    story.append(Spacer(1, 40))

    # Footer message
    # FR6.4: Footer Message Inclusion
    if footer_message:
        story.append(Paragraph("Notes:", header_style))
        story.append(Spacer(1, 5))
        story.append(Paragraph(footer_message, normal_style))

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
