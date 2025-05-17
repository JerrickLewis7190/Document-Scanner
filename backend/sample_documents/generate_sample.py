from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os

def create_sample_passport():
    # Create directory if it doesn't exist
    os.makedirs('sample_documents', exist_ok=True)
    
    # Create the PDF
    c = canvas.Canvas("sample_documents/sample_passport.pdf", pagesize=A4)
    width, height = A4

    # Set up the document
    c.setFillColor(HexColor('#000080'))  # Dark blue color
    c.rect(50, 50, width-100, height-100, fill=1)
    
    # White text
    c.setFillColor(HexColor('#FFFFFF'))
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, height-150, "PASSPORT")
    
    # Passport details
    details = [
        ("Type:", "P"),
        ("Country Code:", "USA"),
        ("Passport No:", "999999999"),
        ("Surname:", "SMITH"),
        ("Given Names:", "JOHN MICHAEL"),
        ("Nationality:", "UNITED STATES OF AMERICA"),
        ("Date of Birth:", "15 JAN 1990"),
        ("Place of Birth:", "NEW YORK, USA"),
        ("Sex:", "M"),
        ("Date of Issue:", "01 JAN 2020"),
        ("Date of Expiry:", "31 DEC 2030"),
        ("Authority:", "U.S. DEPARTMENT OF STATE")
    ]
    
    c.setFont("Helvetica", 12)
    y = height - 200
    for label, value in details:
        c.drawString(100, y, f"{label} {value}")
        y -= 30
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    create_sample_passport() 