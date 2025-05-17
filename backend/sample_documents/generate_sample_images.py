from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta

def create_sample_passport():
    # Create a new image with a dark blue background
    width = 1000
    height = 700
    image = Image.new('RGB', (width, height), color='#000B4F')
    draw = ImageDraw.Draw(image)

    try:
        # Try to use Arial font if available
        font = ImageFont.truetype("arial.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font if Arial is not available
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add passport details
    details = [
        ("PASSPORT", 50),
        ("Type: P", 120),
        ("Country Code: USA", 160),
        ("Passport No: 999999999", 200),
        ("Surname: DOE", 240),
        ("Given Names: JOHN JAMES", 280),
        ("Nationality: UNITED STATES OF AMERICA", 320),
        ("Date of Birth: 01 JAN 1990", 360),
        ("Place of Birth: NEW YORK, USA", 400),
        ("Date of Issue: 01 JAN 2020", 440),
        ("Date of Expiry: 01 JAN 2030", 480),
    ]

    # Add text in white color
    for text, y_pos in details:
        draw.text((50, y_pos), text, fill='white', font=font)

    return image

def create_sample_drivers_license():
    # Create a new image with a gradient background
    width = 850
    height = 550
    image = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add header
    draw.rectangle([0, 0, width, 80], fill='#1C4F9C')
    draw.text((20, 20), "DRIVER LICENSE", fill='white', font=font)

    # Add driver's license details
    details = [
        ("DL NO: X12345678", 100),
        ("CLASS: D", 140),
        ("END: 01/01/2025", 180),
        ("DOB: 01/01/1990", 220),
        ("ISS: 01/01/2020", 260),
        ("NAME: DOE, JOHN JAMES", 300),
        ("ADD: 123 MAIN ST", 340),
        ("       NEW YORK, NY 10001", 380),
        ("REST: NONE", 420),
    ]

    # Add text in black color
    for text, y_pos in details:
        draw.text((20, y_pos), text, fill='black', font=font)

    return image

def create_sample_ead():
    # Create a new image with a white background
    width = 850
    height = 550
    image = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Add header
    draw.rectangle([0, 0, width, 80], fill='#8B0000')
    draw.text((20, 20), "EMPLOYMENT AUTHORIZATION DOCUMENT", fill='white', font=small_font)

    # Add EAD details
    details = [
        ("USCIS#: 999-999-999", 100),
        ("CARD#: AAA1234567890", 140),
        ("NAME: DOE, JOHN JAMES", 180),
        ("DOB: 01/01/1990", 220),
        ("CATEGORY: C08", 260),
        ("VALID FROM: 01/01/2023", 300),
        ("EXPIRES: 01/01/2024", 340),
    ]

    # Add text in black color
    for text, y_pos in details:
        draw.text((20, y_pos), text, fill='black', font=font)

    return image

def main():
    # Create output directory if it doesn't exist
    output_dir = "sample_images"
    os.makedirs(output_dir, exist_ok=True)

    # Generate and save sample documents
    passport = create_sample_passport()
    drivers_license = create_sample_drivers_license()
    ead = create_sample_ead()

    passport.save(os.path.join(output_dir, "sample_passport.png"))
    drivers_license.save(os.path.join(output_dir, "sample_drivers_license.png"))
    ead.save(os.path.join(output_dir, "sample_ead.png"))

    print("Sample documents generated successfully!")

if __name__ == "__main__":
    main() 