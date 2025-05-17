from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_passport_image():
    # Create a new image with a dark blue background
    width = 1000
    height = 700
    image = Image.new('RGB', (width, height), color='#000080')
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
        ("Surname: SMITH", 240),
        ("Given Names: JOHN MICHAEL", 280),
        ("Nationality: UNITED STATES OF AMERICA", 320),
        ("Date of Birth: 15 JAN 1990", 360),
        ("Place of Birth: NEW YORK, USA", 400),
        ("Sex: M", 440),
        ("Date of Issue: 01 JAN 2020", 480),
        ("Date of Expiry: 31 DEC 2030", 520),
        ("Authority: U.S. DEPARTMENT OF STATE", 560)
    ]

    # Draw the text
    for text, y_pos in details:
        if text == "PASSPORT":
            draw.text((50, y_pos), text, fill='white', font=font)
        else:
            draw.text((50, y_pos), text, fill='white', font=small_font)

    # Add a placeholder for photo (rectangle)
    draw.rectangle([700, 120, 900, 320], outline='white', width=2)

    # Create directory if it doesn't exist
    os.makedirs('sample_documents', exist_ok=True)
    
    # Save the image
    image_path = "sample_documents/sample_passport.png"
    image.save(image_path)
    print(f"Sample passport image created at: {image_path}")

if __name__ == "__main__":
    create_sample_passport_image() 