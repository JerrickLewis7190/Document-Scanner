import os
from PIL import Image, ImageDraw, ImageFont

def create_test_image(text, path):
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except IOError:
        font = ImageFont.load_default()
    draw.text((50, 50), text, fill='black', font=font)
    img.save(path)

os.makedirs('test_data/consistency', exist_ok=True)

# Main test images
test_images = [
    ("test_data/dl_fields.png", "DRIVER LICENSE\nDL A1234567\nDOB 01/15/1990\nEXP 01/15/2025\nNAME JOHN A SMITH"),
    ("test_data/ead_test.png", "EMPLOYMENT AUTHORIZATION DOCUMENT\nCARD#: ABC1234567890\nNAME: MARIA GARCIA\nDOB: 05/10/1992\nCATEGORY: C09"),
    ("test_data/pp_test.png", "PASSPORT\nPASSPORT NO: P123456789\nSURNAME: SMITH\nGIVEN NAMES: JOHN\nNATIONALITY: USA\nDOB: 15JAN1985"),
    ("test_data/dl_test.png", "DRIVER LICENSE CLASS D\nNAME: JOHN SMITH\nDOB: 01/15/1985\nDL#: D1234567\nEXP: 01/15/2030")
]
for path, text in test_images:
    create_test_image(text, path)

# Consistency test images (date formats)
date_formats = [
    "01/15/2024", "15/01/2024", "15JAN2024", "2024-01-15", "January 15, 2024"
]
for idx, date in enumerate(date_formats):
    text = f"PASSPORT\nDATE OF BIRTH: {date}"
    create_test_image(text, f"test_data/consistency/date_format_{idx}.png")

# Consistency test images (name formats)
name_variations = [
    "SMITH JOHN", "JOHN SMITH", "SMITH, JOHN", "GARCIA-LOPEZ MARIA", "李 明"
]
for idx, name in enumerate(name_variations):
    text = f"PASSPORT\nNAME: {name}"
    create_test_image(text, f"test_data/consistency/name_format_{idx}.png")

# Mixed format
create_test_image(
    "DRIVER LICENSE\nNAME: John A. Smith\nDOB: January 15, 1985\nDL#: D1234567\nEXP: 01/15/2030\nCLASS: D",
    "test_data/consistency/mixed_format.png"
) 