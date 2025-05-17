from app.utils.ai import check_image_quality
from PIL import Image, ImageDraw
import os

# Test the specific resolution mentioned in the logs (660x426)
print("Testing the specific resolution that was being rejected: 660x426")

# Create test image
filename = "test_660x426.png"
img = Image.new('RGB', (660, 426), color=(240, 240, 240))
draw = ImageDraw.Draw(img)

# Add content to avoid blank image detection
draw.rectangle([(130, 85), (530, 341)], fill=(30, 30, 30))
# Add text-like lines
for i in range(8):
    y_pos = 120 + i * 30
    draw.line([(180, y_pos), (480, y_pos)], fill=(200, 200, 200), width=3)

img.save(filename)

# Verify image dimensions
with Image.open(filename) as check_img:
    print(f"Created image dimensions: {check_img.size[0]}x{check_img.size[1]}")

# Check resolution
is_valid, error_msg = check_image_quality(filename)

print(f"Is valid: {is_valid}")
if error_msg:
    print(f"Error message: {error_msg}")
else:
    print("This image passes validation!")

# Clean up
os.remove(filename) 