from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.units import inch

# Color palette
COLORS = {
    'primary': colors.HexColor("#2E4057"),
    'secondary': colors.HexColor("#6C757D"), 
    'background': colors.HexColor("#F8F9FA"),
    'light_background': colors.HexColor("#E9ECEF"),
    'border': colors.HexColor("#DEE2E6"),
    'white': colors.white,
    'black': colors.black,
}

# Layout dimensions
LAYOUT = {
    'page_margins': {
        'top': 0.75 * inch,
        'bottom': 0.75 * inch,
        'left': 0.75 * inch,
        'right': 0.75 * inch,
    },
    'column_widths': {
        'invoice_info': [1.5 * inch, 2 * inch],
        'contact_table': [3.5 * inch, 3.5 * inch],
        'items_table': [3 * inch, 1 * inch, 1.25 * inch, 1.25 * inch],
    },
    'spacing': {
        'title_bottom': 20,
        'section_bottom': 30,
        'items_header': 10,
        'footer_top': 40,
        'notes_spacing': 5,
    }
}

def get_custom_styles():
    """Returns dictionary of custom paragraph styles"""
    base_styles = getSampleStyleSheet()
    
    return {
        'title': ParagraphStyle(
            "CustomTitle",
            parent=base_styles["Heading1"],
            fontSize=24,
            textColor=COLORS['primary'],
            alignment=TA_CENTER,
            spaceAfter=LAYOUT['spacing']['title_bottom'],
        ),
        
        'header': ParagraphStyle(
            "HeaderStyle",
            parent=base_styles["Normal"],
            fontSize=12,
            textColor=COLORS['primary'],
            fontName="Helvetica-Bold",
        ),
        
        'normal': ParagraphStyle(
            "NormalStyle", 
            parent=base_styles["Normal"], 
            fontSize=10, 
            textColor=COLORS['black']
        ),
    }

def get_table_styles():
    """Returns dictionary of table styles"""
    return {
        'invoice_info': [
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ],
        
        'contact_table': [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ],
        
        'items_table': [
            # Header row styling
            ("BACKGROUND", (0, 0), (-1, 0), COLORS['primary']),
            ("TEXTCOLOR", (0, 0), (-1, 0), COLORS['white']),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            # Data rows styling
            ("FONTNAME", (0, 1), (-1, -3), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -3), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -3), [COLORS['white'], COLORS['background']]),
            # Subtotal and total rows styling
            ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -2), (-1, -1), 11),
            ("BACKGROUND", (0, -1), (-1, -1), COLORS['light_background']),
            # Alignment
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            # Borders
            ("GRID", (0, 0), (-1, -3), 1, COLORS['border']),
            ("LINEBELOW", (0, -2), (-1, -2), 1, COLORS['secondary']),
            ("LINEBELOW", (0, -1), (-1, -1), 2, COLORS['primary']),
            # Padding
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]
    }